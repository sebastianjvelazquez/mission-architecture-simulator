# Database Design Documentation

**Schema Version:** 1.2.0 (Increment 2)
**PostgreSQL Version:** 15+
**ORM:** SQLAlchemy 2.0 (DeclarativeBase)
**Last Updated:** March 28, 2026
**Database Lead:** Person 3

---

## Table of Contents

1. [Overview](#overview)
2. [ER Diagram](#er-diagram)
3. [Table Schemas](#table-schemas)
4. [Indexes](#indexes)
5. [Data Integrity](#data-integrity)
6. [Cascade Delete Behaviour](#cascade-delete-behaviour)
7. [Connection & Pooling](#connection--pooling)
8. [Query Monitoring](#query-monitoring)
9. [Backup & Restore](#backup--restore)
10. [Migration Strategy](#migration-strategy)
11. [Data Verification Queries](#data-verification-queries)
12. [Troubleshooting](#troubleshooting)

---

## Overview

Five tables store all persistent state for the Mission System Security Architecture Simulator.

| Table | Purpose |
|---|---|
| `architectures` | Top-level mission system containers |
| `components` | Nodes in an architecture graph |
| `flows` | Directed edges between components |
| `scenarios` | Saved simulation scenario inputs per architecture |
| `simulation_results` | Persisted simulation outputs per scenario |

Increment 2 adds robust persistence and validation for scenario workflows.
All new CRUD operations use endpoint-level database exception handling with
rollback on write failures and meaningful 409/500 responses.

Tables are created automatically at startup via `Base.metadata.create_all()` in `backend/app/database.py`. No manual SQL is required for a fresh deployment.

---

## ER Diagram

```
┌──────────────────────────────────────────┐
│               architectures              │
│  ────────────────────────────────────    │
│  PK  id              INTEGER             │
│      name            VARCHAR(255)  NN    │
│      description     TEXT                │
│      properties      JSONB               │
│      created_at      TIMESTAMPTZ   NN    │
│      updated_at      TIMESTAMPTZ   NN    │
└─────────────┬────────────────────────────┘
              │ 1
              │ ON DELETE CASCADE
              │ N
    ┌─────────┴────────────────────────────────┐
    │                                          │
    ▼                                          ▼
┌────────────────────────────────┐   ┌────────────────────────────────┐
│           components           │   │             flows               │
│  ────────────────────────────  │   │  ────────────────────────────  │
│  PK  id              INTEGER   │   │  PK  id              INTEGER   │
│  FK  architecture_id INTEGER NN│   │  FK  architecture_id INTEGER NN│
│      component_id    VARCHAR NN│   │  FK  source_comp_id  INTEGER NN│
│      name            VARCHAR NN│   │  FK  target_comp_id  INTEGER NN│
│      component_type  VARCHAR NN│   │      data_type       VARCHAR   │
│      criticality     INTEGER NN│   │      cia_requirement VARCHAR   │
│      position_x      FLOAT     │   │      latency_sens.   VARCHAR   │
│      position_y      FLOAT     │   │      properties      JSONB     │
│      properties      JSONB     │   │      created_at      TIMESTAMPTZ│
│      created_at      TIMESTAMPTZ│  │      updated_at      TIMESTAMPTZ│
│      updated_at      TIMESTAMPTZ│  └────────────────────────────────┘
└────────────────────────────────┘         │              │
        ▲                                  │              │
        │    source_component_id FK ───────┘              │
        │    target_component_id FK ──────────────────────┘
        │    (both ON DELETE CASCADE)
        └── One component can appear as source or target in many flows
```

**Cardinalities:**

| Relationship | Type | Notes |
|---|---|---|
| Architecture → Components | 1 : N | Deleting architecture cascades to components |
| Architecture → Flows | 1 : N | Deleting architecture cascades to flows |
| Component → Flows (source) | 1 : N | Deleting component cascades its outgoing flows |
| Component → Flows (target) | 1 : N | Deleting component cascades its incoming flows |

---

### dbdiagram.io DBML

Paste this at [dbdiagram.io](https://dbdiagram.io) to generate a visual ER diagram.

```dbml
Table architectures {
  id          integer      [pk, increment, not null]
  name        varchar(255) [not null, note: "Architecture display name"]
  description text
  properties  jsonb        [note: "Free-form metadata, defaults to {}"]
  created_at  timestamptz  [not null]
  updated_at  timestamptz  [not null]

  indexes {
    name         [name: "ix_architectures_name"]
    created_at   [name: "ix_architectures_created_at"]
  }
}

Table components {
  id               integer      [pk, increment, not null]
  architecture_id  integer      [not null, ref: > architectures.id]
  component_id     varchar(255) [not null, note: "Frontend UUID/slug"]
  name             varchar(255) [not null]
  component_type   varchar(50)  [not null, note: "Sensor|Compute|CommsLink|Control|Storage|External"]
  criticality      integer      [not null, default: 5, note: "1 (low) to 10 (critical)"]
  position_x       float
  position_y       float
  properties       jsonb
  created_at       timestamptz  [not null]
  updated_at       timestamptz  [not null]

  indexes {
    architecture_id  [name: "ix_components_architecture_id"]
    component_id     [name: "ix_components_component_id"]
    component_type   [name: "ix_components_component_type"]
  }
}

Table flows {
  id                   integer     [pk, increment, not null]
  architecture_id      integer     [not null, ref: > architectures.id]
  source_component_id  integer     [not null, ref: > components.id]
  target_component_id  integer     [not null, ref: > components.id]
  data_type            varchar(100)[note: "e.g. telemetry, commands, video"]
  cia_requirement      varchar(50) [note: "confidentiality | integrity | availability"]
  latency_sensitivity  varchar(20) [note: "low | medium | high"]
  properties           jsonb
  created_at           timestamptz [not null]
  updated_at           timestamptz [not null]

  indexes {
    architecture_id      [name: "ix_flows_architecture_id"]
    source_component_id  [name: "ix_flows_source_component_id"]
    target_component_id  [name: "ix_flows_target_component_id"]
  }
}
```

---

## Table Schemas

### 1. `architectures`

**Purpose:** Top-level container for a mission system. Each architecture is an independent directed graph of components and flows.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `INTEGER` | NOT NULL | auto-increment | Primary key |
| `name` | `VARCHAR(255)` | NOT NULL | — | Display name, e.g. "UAV Sensor Network" |
| `description` | `TEXT` | NULL | — | Free-text description |
| `properties` | `JSONB` | NULL | `{}` | Flexible metadata (tags, version, owner, etc.) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `now()` | Set once on insert |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `now()` | Auto-updated on every ORM write |

**Constraints:**
- `PRIMARY KEY (id)`
- `name NOT NULL` — every architecture must have a name

**ORM relationships:**
- `architecture.components` → list of `Component` (selectin loaded)
- `architecture.flows` → list of `Flow` (selectin loaded)

---

### 2. `components`

**Purpose:** A node in the architecture graph. Represents a physical or logical system element (sensor, compute node, communications link, etc.).

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `INTEGER` | NOT NULL | auto-increment | Primary key (DB integer) |
| `architecture_id` | `INTEGER` | NOT NULL | — | FK → `architectures.id` ON DELETE CASCADE |
| `component_id` | `VARCHAR(255)` | NOT NULL | — | Frontend-generated UUID/slug (used by flows at POST time) |
| `name` | `VARCHAR(255)` | NOT NULL | — | Human-readable label |
| `component_type` | `VARCHAR(50)` | NOT NULL | — | One of: `Sensor`, `Compute`, `CommsLink`, `Control`, `Storage`, `External` |
| `criticality` | `INTEGER` | NOT NULL | `5` | Mission criticality score: 1 (low) – 10 (critical) |
| `position_x` | `FLOAT` | NULL | — | Canvas X coordinate for the diagram editor |
| `position_y` | `FLOAT` | NULL | — | Canvas Y coordinate for the diagram editor |
| `properties` | `JSONB` | NULL | `{}` | Extensible metadata (vendor, firmware, etc.) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `now()` | Set once on insert |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `now()` | Auto-updated on every ORM write |

**Constraints:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (architecture_id) REFERENCES architectures(id) ON DELETE CASCADE`
- `criticality NOT NULL` — enforced by ORM (`ge=1, le=10` in Pydantic schema)

**Note on `component_id` vs `id`:** `id` is the integer database PK used for FK references. `component_id` is the string slug/UUID the frontend assigns (e.g. `"sensor-1"` or a UUID4). Flows in the POST request reference components by `component_id`, which the API resolves to the integer `id` after insert.

**ORM relationships:**
- `component.architecture` → parent `Architecture`
- `component.outgoing_flows` → flows where this component is the source
- `component.incoming_flows` → flows where this component is the target

**Sample `properties` JSONB:**
```json
{
  "vendor": "Raytheon",
  "firmware_version": "3.2.1",
  "location": "fuselage"
}
```

---

### 3. `flows`

**Purpose:** A directed edge in the architecture graph. Represents a data or control signal path between two components.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `INTEGER` | NOT NULL | auto-increment | Primary key |
| `architecture_id` | `INTEGER` | NOT NULL | — | FK → `architectures.id` ON DELETE CASCADE |
| `source_component_id` | `INTEGER` | NOT NULL | — | FK → `components.id` ON DELETE CASCADE (edge origin) |
| `target_component_id` | `INTEGER` | NOT NULL | — | FK → `components.id` ON DELETE CASCADE (edge destination) |
| `data_type` | `VARCHAR(100)` | NULL | — | What is transmitted: `telemetry`, `commands`, `video`, etc. |
| `cia_requirement` | `VARCHAR(50)` | NULL | — | Primary CIA concern: `confidentiality`, `integrity`, `availability` |
| `latency_sensitivity` | `VARCHAR(20)` | NULL | — | `low`, `medium`, or `high` |
| `properties` | `JSONB` | NULL | `{}` | Extensible metadata (bandwidth, protocol, encryption, etc.) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `now()` | Set once on insert |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `now()` | Auto-updated on every ORM write |

**Constraints:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (architecture_id) REFERENCES architectures(id) ON DELETE CASCADE`
- `FOREIGN KEY (source_component_id) REFERENCES components(id) ON DELETE CASCADE`
- `FOREIGN KEY (target_component_id) REFERENCES components(id) ON DELETE CASCADE`

**ORM relationships:**
- `flow.architecture` → parent `Architecture`
- `flow.source_component` → `Component` at edge origin
- `flow.target_component` → `Component` at edge destination

**Sample `properties` JSONB:**
```json
{
  "bandwidth_mbps": 100,
  "protocol": "AES-256",
  "encrypted": true
}
```

---

## Indexes

All indexes are B-tree, declared in `__table_args__` on each ORM model and created automatically with `create_all()`.

| Index name | Table | Column(s) | Purpose |
|---|---|---|---|
| `ix_architectures_name` | `architectures` | `name` | Name-based search/filter |
| `ix_architectures_created_at` | `architectures` | `created_at` | Default sort (newest first) on list endpoint |
| `ix_components_architecture_id` | `components` | `architecture_id` | Fast component lookup by parent architecture |
| `ix_components_component_id` | `components` | `component_id` | Slug lookup during flow resolution at POST time |
| `ix_components_component_type` | `components` | `component_type` | Filter components by type in analysis/simulator |
| `ix_flows_architecture_id` | `flows` | `architecture_id` | Load all flows for an architecture |
| `ix_flows_source_component_id` | `flows` | `source_component_id` | Graph traversal: outgoing edges from a node |
| `ix_flows_target_component_id` | `flows` | `target_component_id` | Graph traversal: incoming edges to a node |
| `ix_scenarios_architecture_id` | `scenarios` | `architecture_id` | List scenarios for an architecture |
| `ix_scenarios_scenario_type` | `scenarios` | `scenario_type` | Filter/query scenarios by type |
| `ix_scenarios_target_component_id` | `scenarios` | `target_component_id` | Lookup scenarios by target component |
| `ix_scenarios_created_at` | `scenarios` | `created_at` | Newest-first scenario retrieval |
| `ix_simulation_results_scenario_id` | `simulation_results` | `scenario_id` | Load all results for a scenario |
| `ix_simulation_results_created_at` | `simulation_results` | `created_at` | Newest-first result retrieval |

---

## Data Integrity

### Constraint Summary

| Rule | Enforced by |
|---|---|
| `architectures.name` cannot be empty | DB NOT NULL + Pydantic `str` field |
| `components.criticality` between 1 and 10 | Pydantic `Field(ge=1, le=10)` on `ComponentCreate` |
| `component_id` slugs must be unique within a POST request | Python check in `create_architecture()` before any DB write |
| Flow source/target must reference components in the same request | Python check before any DB write |
| Scenario type must be one of supported values before insert | API validation in scenarios endpoint |
| Scenario parameters are validated by scenario type before insert | API validation in scenarios endpoint |
| Deleting an architecture removes all its children | `ON DELETE CASCADE` on `components.architecture_id` and `flows.architecture_id` |
| Deleting a component removes its flows | `ON DELETE CASCADE` on `flows.source_component_id` and `flows.target_component_id` |
| Deleting a scenario removes persisted simulation results | `ON DELETE CASCADE` on `simulation_results.scenario_id` |
| No orphaned components or flows | Cascade + `passive_deletes=True` on all ORM relationships |

### Error Handling

| Exception | HTTP status | When it occurs |
|---|---|---|
| `IntegrityError` (unique violation) | 409 Conflict | Duplicate insert violates a unique constraint |
| `IntegrityError` (not-null violation) | 409 Conflict | A required column receives NULL |
| `IntegrityError` (FK violation) | 409 Conflict | Referenced row does not exist |
| `SQLAlchemyError` (generic) | 500 Internal Server Error | Connection dropped, timeout, unexpected DB error |
| Rollback | triggered on all of the above | Session is always rolled back before the HTTP response is sent |

The same exception strategy is applied across new Increment 2 endpoints in
architectures and scenarios routers, including create, update, delete, and list
paths that touch persisted scenario data.

All database operations are wrapped in `try / except IntegrityError / except SQLAlchemyError` blocks. A global `@app.exception_handler(SQLAlchemyError)` in `main.py` acts as a safety net for any error that escapes endpoint-level handling.

---

## Cascade Delete Behaviour

```sql
-- Deleting an architecture removes all its components and flows automatically:
DELETE FROM architectures WHERE id = 1;
-- Removes: the architecture row, all component rows with architecture_id=1,
--          and all flow rows with architecture_id=1.

-- Deleting a component removes its outgoing and incoming flows automatically:
DELETE FROM components WHERE id = 5;
-- Removes: the component row and all flows where
--          source_component_id=5 OR target_component_id=5.
```

Self-referential flow clean-up works because both `source_component_id` and `target_component_id` carry separate `ON DELETE CASCADE` foreign keys to `components`.

---

## Connection & Pooling

Configured in `backend/app/database.py`:

| Setting | Value | Notes |
|---|---|---|
| `pool_size` | 5 | Core persistent connections |
| `max_overflow` | 10 | Extra connections under burst load (max 15 total) |
| `pool_timeout` | 30 s | How long a request waits for a free connection before erroring |
| `pool_pre_ping` | True | Issues `SELECT 1` before handing out a connection; drops stale connections |
| `autocommit` | False | Transactions must be explicitly committed |
| `autoflush` | False | ORM changes are not flushed until explicitly called |

**Connection string (from `.env`):**
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mission_simulator
```

Docker Compose overrides this with `@db:5432` (the internal service name) when running containerised.

---

## Query Monitoring

`database.py` registers two SQLAlchemy engine events that timestamp every query:

- `before_cursor_execute` — stores `time.perf_counter()` on the connection's info dict.
- `after_cursor_execute` — computes elapsed ms and:
  - Logs `WARNING "Slow query (Xms): <truncated SQL>"` if elapsed ≥ 200 ms.
  - Logs `DEBUG "Query OK (Xms)"` otherwise.

The threshold is controlled by `_SLOW_QUERY_THRESHOLD_MS = 200` in `database.py`.

An HTTP middleware in `main.py` adds `X-Process-Time-Ms` to every response header and logs:
```
GET /architectures/1 completed in 14.2 ms (status=200)
```

---

## Backup & Restore

### Backup

**Full logical backup with `pg_dump`:**

```powershell
# Dump to a compressed file (recommended for production)
docker exec mission-simulator-db pg_dump `
  -U postgres `
  -d mission_simulator `
  --format=custom `
  --compress=9 `
  --file=/tmp/mission_simulator_backup.dump

# Copy the dump out of the container to the host
docker cp mission-simulator-db:/tmp/mission_simulator_backup.dump `
  ./backups/mission_simulator_$(Get-Date -Format 'yyyyMMdd_HHmmss').dump
```

**Plain SQL backup (human-readable):**

```powershell
docker exec mission-simulator-db pg_dump `
  -U postgres `
  -d mission_simulator `
  --format=plain `
  > ./backups/mission_simulator_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql
```

**Schema-only backup (no data):**

```powershell
docker exec mission-simulator-db pg_dump `
  -U postgres `
  -d mission_simulator `
  --schema-only `
  > ./backups/schema_only.sql
```

### Restore

**Restore from a custom-format dump:**

```powershell
# Copy dump into container, then restore
docker cp ./backups/mission_simulator_20260222.dump `
  mission-simulator-db:/tmp/restore.dump

docker exec mission-simulator-db pg_restore `
  -U postgres -d mission_simulator --clean --if-exists /tmp/restore.dump
```

**Restore from a plain SQL backup:**

```powershell
Get-Content .\backups\mission_simulator_20260222.sql |
  docker exec -i mission-simulator-db psql -U postgres -d mission_simulator
```

### Backup Strategy (Increment 1)

| Scenario | Approach |
|---|---|
| Local development | `pg_dump` plain SQL before any destructive test |
| CI/CD pipeline | Schema-only dump as an artifact on every merged PR |
| Staging/production (future) | Scheduled `pg_dump --format=custom` + Docker volume snapshot |

### Re-creating the database from scratch

```powershell
docker compose down -v          # removes the postgres_data volume
docker compose up -d db         # creates a fresh postgres container
# Tables are auto-created on next backend startup via init_db()
```

---

## Migration Strategy

### Increment 1: `create_all()` (no Alembic)

Tables are created by `Base.metadata.create_all(bind=engine)` at startup (`init_db()` in `database.py`). This is appropriate for Increment 1 because the schema is new and there is no production data to preserve.

`create_all()` is **additive only** — it creates missing tables but never drops or alters existing ones:
- Adding a new table: safe, runs on next startup automatically.
- Adding a nullable column to an existing table: requires a manual `ALTER TABLE` or Alembic.
- Renaming or dropping a column: requires Alembic.

### Post-Increment 1: Alembic

```bash
cd backend
pip install alembic
alembic init alembic

# Edit alembic/env.py:
# from app.models.architecture import Base
# target_metadata = Base.metadata

# Generate a migration from ORM changes
alembic revision --autogenerate -m "describe the change"

# Apply pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1
```

**Migration rules for the team:**
1. Never edit an existing migration file after it has been merged.
2. One migration per PR — keep diffs small and reviewable.
3. Include both `upgrade()` and `downgrade()` in every migration.
4. Test `upgrade` + `downgrade` locally before pushing.

---

## Data Verification Queries

Run these inside the PostgreSQL shell:
```powershell
docker exec -it mission-simulator-db psql -U postgres -d mission_simulator
```

**Verify tables exist:**
```sql
\dt
```

**Verify all indexes are present:**
```sql
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

Expected output includes:
```
 architectures | architectures_pkey
 architectures | ix_architectures_created_at
 architectures | ix_architectures_name
 components    | components_pkey
 components    | ix_components_architecture_id
 components    | ix_components_component_id
 components    | ix_components_component_type
 flows         | flows_pkey
 flows         | ix_flows_architecture_id
 flows         | ix_flows_source_component_id
 flows         | ix_flows_target_component_id
```

**Verify foreign keys:**
```sql
SELECT conname          AS constraint_name,
       conrelid::regclass  AS "table",
       confrelid::regclass AS references
FROM   pg_constraint
WHERE  contype = 'f'
ORDER  BY "table";
```

**Count records per table:**
```sql
SELECT 'architectures' AS tbl, COUNT(*) FROM architectures
UNION ALL
SELECT 'components',           COUNT(*) FROM components
UNION ALL
SELECT 'flows',                COUNT(*) FROM flows;
```

**Check cascade is working (dry run — do not run on real data):**
```sql
BEGIN;
  DELETE FROM architectures WHERE id = <test_id>;
  SELECT COUNT(*) FROM components WHERE architecture_id = <test_id>; -- expect 0
  SELECT COUNT(*) FROM flows     WHERE architecture_id = <test_id>; -- expect 0
ROLLBACK;
```

**Verify no dangling flow FK references:**
```sql
-- Flows whose source component no longer exists (should return 0 rows)
SELECT f.id FROM flows f
LEFT JOIN components c ON c.id = f.source_component_id
WHERE c.id IS NULL;

-- Flows whose target component no longer exists (should return 0 rows)
SELECT f.id FROM flows f
LEFT JOIN components c ON c.id = f.target_component_id
WHERE c.id IS NULL;
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `relation "architectures" does not exist` | Tables not created yet | Start the backend so `init_db()` runs, or run `docker compose up` |
| `duplicate key value violates unique constraint` | Inserting a row that breaks a unique index | API returns 409 with a descriptive message; check for existing data |
| `null value in column violates not-null constraint` | Missing required field in payload | Check the Pydantic 422 response body for the exact field |
| `could not connect to server` | Postgres container not running | `docker compose up -d db` and wait ~5 s |
| `FATAL: database "mission_simulator" does not exist` | Volume wiped before DB was created | `docker compose up -d db` — `POSTGRES_DB` env var creates it automatically |
| Slow queries logged as WARNING | Query missing an index or large table scan | Check `EXPLAIN ANALYZE` output; add an index if appropriate |
| `alembic.util.exc.CommandError: Can't locate revision` | Migration history mismatch | `alembic stamp head` to mark current DB as up-to-date, then retry |
