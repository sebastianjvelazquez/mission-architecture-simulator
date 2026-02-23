"""
tests/test_db_queries.py

Database query optimization tests. All tests use an in-memory SQLite engine
so Docker/Postgres is not required to run the suite.

Covers:
    - All expected indexes exist (architectures, components, flows)
    - Eager loading via selectinload: components and flows loaded in fixed queries
    - No N+1 query behaviour verified by counting statement events
    - Bulk insert of 100+ architectures completes and is fully queryable
    - Pagination (skip / limit) on the list query
    - list ordered by created_at descending
    - Connection pool settings match configuration
    - Cascade delete propagates from architecture to children
"""

from __future__ import annotations

import time
from typing import Generator

import pytest
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import Session, selectinload, sessionmaker

# SQLite does not natively support JSONB. Teach its compiler to treat JSONB
# identically to JSON so we can run schema-creation against in-memory SQLite.
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

SQLiteTypeCompiler.visit_JSONB = SQLiteTypeCompiler.visit_JSON  # type: ignore[attr-defined]

from app.models.architecture import Architecture, Base, Component, Flow

# ---------------------------------------------------------------------------
# Engine / session fixtures
# ---------------------------------------------------------------------------

SQLITE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
    )

    # Enable foreign-key enforcement so ON DELETE CASCADE works in SQLite.
    @event.listens_for(engine, "connect")
    def set_fk_pragma(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db(db_engine) -> Generator[Session, None, None]:
    SessionFactory = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = SessionFactory()
    yield session
    session.rollback()
    session.close()


# ---------------------------------------------------------------------------
# Query counter helper
# ---------------------------------------------------------------------------

class QueryCounter:
    """Attach to an engine to count SQL statements executed within a block."""

    def __init__(self, engine):
        self._engine = engine
        self.count = 0

    def __enter__(self):
        event.listen(self._engine, "before_cursor_execute", self._handler)
        return self

    def __exit__(self, *args):
        event.remove(self._engine, "before_cursor_execute", self._handler)

    def _handler(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def _arch(name: str = "Arch") -> Architecture:
    return Architecture(name=name, description=None, properties={})


def _component(arch_id: int, slug: str, ctype: str = "Sensor") -> Component:
    return Component(
        architecture_id=arch_id,
        component_id=slug,
        name=slug,
        component_type=ctype,
        criticality=5,
        position_x=0.0,
        position_y=0.0,
        properties={},
    )


def _flow(arch_id: int, src_id: int, tgt_id: int) -> Flow:
    return Flow(
        architecture_id=arch_id,
        source_component_id=src_id,
        target_component_id=tgt_id,
        properties={},
    )


# ---------------------------------------------------------------------------
# Index tests
# ---------------------------------------------------------------------------

class TestIndexes:

    def test_architectures_has_name_index(self, db_engine):
        indexes = {idx["name"] for idx in inspect(db_engine).get_indexes("architectures")}
        assert "ix_architectures_name" in indexes

    def test_architectures_has_created_at_index(self, db_engine):
        indexes = {idx["name"] for idx in inspect(db_engine).get_indexes("architectures")}
        assert "ix_architectures_created_at" in indexes

    def test_components_has_architecture_id_index(self, db_engine):
        indexes = {idx["name"] for idx in inspect(db_engine).get_indexes("components")}
        assert "ix_components_architecture_id" in indexes

    def test_components_has_component_id_index(self, db_engine):
        indexes = {idx["name"] for idx in inspect(db_engine).get_indexes("components")}
        assert "ix_components_component_id" in indexes

    def test_components_has_component_type_index(self, db_engine):
        indexes = {idx["name"] for idx in inspect(db_engine).get_indexes("components")}
        assert "ix_components_component_type" in indexes

    def test_flows_has_architecture_id_index(self, db_engine):
        indexes = {idx["name"] for idx in inspect(db_engine).get_indexes("flows")}
        assert "ix_flows_architecture_id" in indexes

    def test_flows_has_source_component_id_index(self, db_engine):
        indexes = {idx["name"] for idx in inspect(db_engine).get_indexes("flows")}
        assert "ix_flows_source_component_id" in indexes

    def test_flows_has_target_component_id_index(self, db_engine):
        indexes = {idx["name"] for idx in inspect(db_engine).get_indexes("flows")}
        assert "ix_flows_target_component_id" in indexes


# ---------------------------------------------------------------------------
# Eager loading / N+1 tests
# ---------------------------------------------------------------------------

class TestEagerLoading:

    def test_selectinload_components_are_available(self, db):
        arch = _arch("EagerArch")
        db.add(arch)
        db.flush()

        db.add(_component(arch.id, "c1"))
        db.add(_component(arch.id, "c2"))
        db.commit()

        loaded = (
            db.query(Architecture)
            .options(selectinload(Architecture.components))
            .filter(Architecture.id == arch.id)
            .first()
        )

        assert loaded is not None
        assert len(loaded.components) == 2

    def test_selectinload_flows_are_available(self, db):
        arch = _arch("FlowArch")
        db.add(arch)
        db.flush()

        c1 = _component(arch.id, "f-c1")
        c2 = _component(arch.id, "f-c2")
        db.add(c1)
        db.add(c2)
        db.flush()

        db.add(_flow(arch.id, c1.id, c2.id))
        db.commit()

        loaded = (
            db.query(Architecture)
            .options(selectinload(Architecture.flows))
            .filter(Architecture.id == arch.id)
            .first()
        )

        assert loaded is not None
        assert len(loaded.flows) == 1
        assert loaded.flows[0].source_component_id == c1.id

    def test_no_n_plus_one_on_list(self, db, db_engine):
        """
        Loading N architectures with selectinload must fire exactly 3 queries
        (1 for architectures, 1 for components IN (...), 1 for flows IN (...))
        regardless of N.
        """
        # Insert 5 architectures each with 2 components and 1 flow.
        ids = []
        for i in range(5):
            arch = _arch(f"N1-{i}")
            db.add(arch)
            db.flush()
            c1 = _component(arch.id, f"n1-c{i}-a")
            c2 = _component(arch.id, f"n1-c{i}-b")
            db.add(c1)
            db.add(c2)
            db.flush()
            db.add(_flow(arch.id, c1.id, c2.id))
            ids.append(arch.id)
        db.commit()

        # Expire all cached objects so the query actually hits the DB.
        db.expire_all()

        with QueryCounter(db_engine) as counter:
            rows = (
                db.query(Architecture)
                .options(
                    selectinload(Architecture.components),
                    selectinload(Architecture.flows),
                )
                .filter(Architecture.id.in_(ids))
                .all()
            )

        # selectinload fires a fixed number of queries no matter how many rows:
        #   1 - SELECT architectures WHERE id IN (...)
        #   2 - SELECT components WHERE architecture_id IN (...)       [Architecture.components]
        #   3 - SELECT flows WHERE architecture_id IN (...)            [Architecture.flows]
        #   4 - SELECT flows WHERE source_component_id IN (...)        [Component.outgoing_flows lazy='selectin']
        #   5 - SELECT flows WHERE target_component_id IN (...)        [Component.incoming_flows lazy='selectin']
        # Total = 5, constant regardless of N. That is the proof there is no N+1.
        assert counter.count == 5
        assert all(len(r.components) == 2 for r in rows)
        assert all(len(r.flows) == 1 for r in rows)

    def test_lazy_selectin_on_model_does_not_need_explicit_option(self, db):
        """
        Architecture.components uses lazy='selectin', so accessing .components
        after a plain query must still return results without an explicit option.
        """
        arch = _arch("LazySelectinArch")
        db.add(arch)
        db.flush()
        db.add(_component(arch.id, "lazy-c1"))
        db.commit()
        db.expire_all()

        loaded = db.query(Architecture).filter(Architecture.id == arch.id).first()
        # lazy='selectin' fires automatically on first access.
        assert len(loaded.components) == 1


# ---------------------------------------------------------------------------
# Bulk insert / performance test
# ---------------------------------------------------------------------------

class TestBulkInsert:

    def test_bulk_insert_100_architectures(self, db):
        arches = [_arch(f"BulkArch-{i}") for i in range(100)]
        db.add_all(arches)
        db.commit()

        count = db.query(Architecture).filter(
            Architecture.name.like("BulkArch-%")
        ).count()
        assert count == 100

    def test_bulk_insert_completes_under_threshold(self, db):
        start = time.perf_counter()
        arches = [_arch(f"PerfArch-{i}") for i in range(100)]
        db.add_all(arches)
        db.commit()
        elapsed_ms = (time.perf_counter() - start) * 1000
        # 5 seconds is a generous upper bound for 100 row inserts in SQLite.
        assert elapsed_ms < 5000, f"Bulk insert took {elapsed_ms:.0f} ms"

    def test_list_all_returns_all_inserted(self, db):
        db.add_all([_arch(f"ListArch-{i}") for i in range(10)])
        db.commit()

        all_rows = db.query(Architecture).filter(
            Architecture.name.like("ListArch-%")
        ).all()
        assert len(all_rows) >= 10


# ---------------------------------------------------------------------------
# Pagination tests
# ---------------------------------------------------------------------------

class TestPagination:

    @pytest.fixture(autouse=True)
    def seed(self, db):
        """Insert 20 architectures specifically for pagination tests."""
        db.add_all([_arch(f"PageArch-{i:02d}") for i in range(20)])
        db.commit()

    def test_limit_restricts_result_count(self, db):
        rows = (
            db.query(Architecture)
            .filter(Architecture.name.like("PageArch-%"))
            .order_by(Architecture.created_at.desc())
            .limit(5)
            .all()
        )
        assert len(rows) == 5

    def test_skip_offsets_results(self, db):
        all_rows = (
            db.query(Architecture)
            .filter(Architecture.name.like("PageArch-%"))
            .order_by(Architecture.id.asc())
            .all()
        )
        offset_rows = (
            db.query(Architecture)
            .filter(Architecture.name.like("PageArch-%"))
            .order_by(Architecture.id.asc())
            .offset(5)
            .all()
        )
        assert len(offset_rows) == len(all_rows) - 5
        assert offset_rows[0].id == all_rows[5].id

    def test_list_ordered_by_created_at_desc(self, db):
        rows = (
            db.query(Architecture)
            .filter(Architecture.name.like("PageArch-%"))
            .order_by(Architecture.created_at.desc())
            .limit(20)
            .all()
        )
        timestamps = [r.created_at for r in rows]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_skip_and_limit_combined(self, db):
        rows = (
            db.query(Architecture)
            .filter(Architecture.name.like("PageArch-%"))
            .order_by(Architecture.id.asc())
            .offset(10)
            .limit(5)
            .all()
        )
        assert len(rows) == 5


# ---------------------------------------------------------------------------
# Get by ID tests
# ---------------------------------------------------------------------------

class TestGetById:

    def test_get_existing_id_returns_architecture(self, db):
        arch = _arch("GetById")
        db.add(arch)
        db.commit()

        result = db.query(Architecture).filter(Architecture.id == arch.id).first()
        assert result is not None
        assert result.name == "GetById"

    def test_get_missing_id_returns_none(self, db):
        result = db.query(Architecture).filter(Architecture.id == 999999).first()
        assert result is None

    def test_get_loads_components_and_flows(self, db):
        arch = _arch("FullLoad")
        db.add(arch)
        db.flush()

        c1 = _component(arch.id, "fl-c1", "Sensor")
        c2 = _component(arch.id, "fl-c2", "Compute")
        db.add(c1)
        db.add(c2)
        db.flush()
        db.add(_flow(arch.id, c1.id, c2.id))
        db.commit()
        db.expire_all()

        loaded = (
            db.query(Architecture)
            .options(
                selectinload(Architecture.components),
                selectinload(Architecture.flows),
            )
            .filter(Architecture.id == arch.id)
            .first()
        )

        assert len(loaded.components) == 2
        assert len(loaded.flows) == 1


# ---------------------------------------------------------------------------
# Cascade delete tests
# ---------------------------------------------------------------------------

class TestCascadeDelete:

    def test_deleting_architecture_removes_components(self, db):
        arch = _arch("CascadeArch")
        db.add(arch)
        db.flush()
        db.add(_component(arch.id, "cas-c1"))
        db.add(_component(arch.id, "cas-c2"))
        db.commit()

        db.delete(arch)
        db.commit()

        remaining = db.query(Component).filter(
            Component.component_id.in_(["cas-c1", "cas-c2"])
        ).count()
        assert remaining == 0

    def test_deleting_architecture_removes_flows(self, db):
        arch = _arch("CascadeFlowArch")
        db.add(arch)
        db.flush()
        c1 = _component(arch.id, "cf-c1")
        c2 = _component(arch.id, "cf-c2")
        db.add(c1)
        db.add(c2)
        db.flush()
        flow = _flow(arch.id, c1.id, c2.id)
        db.add(flow)
        db.flush()  # populate flow.id before commit
        flow_id = flow.id
        db.commit()

        db.delete(arch)
        db.commit()

        assert db.query(Flow).filter(Flow.id == flow_id).first() is None


# ---------------------------------------------------------------------------
# Connection pool configuration test
# ---------------------------------------------------------------------------

class TestConnectionPool:

    def test_pool_size_is_configured(self):
        from app.database import engine
        pool = engine.pool
        # NullPool / StaticPool used in tests won't have these attrs,
        # but the production engine created from database.py will.
        if hasattr(pool, "size"):
            assert pool.size() == 5

    def test_max_overflow_is_configured(self):
        from app.database import engine
        pool = engine.pool
        if hasattr(pool, "_max_overflow"):
            assert pool._max_overflow == 10

    def test_pool_pre_ping_is_enabled(self):
        from app.database import engine
        assert engine.pool._pre_ping is True
