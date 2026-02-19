# Database Schema Documentation

## Overview

This document describes the PostgreSQL database schema for the Mission System Security Architecture Simulator.

**Schema Version:** 1.0.0 (Increment 1)  
**PostgreSQL Version:** 15+  
**Last Updated:** February 19, 2026

---

## Quick Reference

### Tables
- **architectures** - Top-level mission systems
- **components** - Nodes in architecture graphs (sensors, compute, etc.)
- **flows** - Directed edges between components (data/control flows)

### Key Features
- ✅ Full ACID compliance
- ✅ Referential integrity with cascading deletes
- ✅ JSONB for flexible properties
- ✅ Automatic timestamp management
- ✅ Performance-optimized indexes (B-tree + GIN)
- ✅ Graph-friendly structure for NetworkX

---

## Entity Relationship Diagram (Text)

```
┌──────────────────────────────────────┐
│           architectures              │
│  ──────────────────────────────────  │
│  PK: id (serial)                     │
│  name (varchar)                      │
│  description (text)                  │
│  created_at, updated_at (timestamp)  │
└──────────┬───────────────────────────┘
           │
           │ 1:N (CASCADE DELETE)
           │
    ┌──────┴──────────────────┐
    │                         │
    ▼                         ▼
┌─────────────────┐     ┌─────────────────┐
│   components    │     │      flows      │
│  ─────────────  │     │  ─────────────  │
│  PK: id         │     │  PK: id         │
│  FK: arch_id ───┼─────┼─→FK: arch_id    │
│  name           │     │  FK: source ────┼──┐
│  type           │     │  FK: target ────┼──┤
│  properties     │     │  flow_type      │  │
│  position_x/y   │     │  properties     │  │
│  timestamps     │     │  timestamps     │  │
└─────────────────┘     └─────────────────┘  │
       ▲                                      │
       │                                      │
       └──────────────────────────────────────┘
           (Flows reference components)
```

**Cardinalities:**
- 1 Architecture → N Components
- 1 Architecture → N Flows
- 1 Component → N Flows (as source)
- 1 Component → N Flows (as target)

---

## Table Schemas

### 1. `architectures`

**Purpose:** Store top-level mission systems created by users.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NOT NULL | auto | Primary key |
| `name` | VARCHAR(255) | NOT NULL | - | Architecture name (e.g., "UAV System") |
| `description` | TEXT | NULL | - | Optional description |
| `created_at` | TIMESTAMP WITH TIME ZONE | NULL | `CURRENT_TIMESTAMP` | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NULL | `CURRENT_TIMESTAMP` | Last update (auto-updated) |

**Constraints:**
- `PRIMARY KEY (id)`
- `CHECK (char_length(name) > 0)` - Name cannot be empty

**Indexes:**
- `idx_architectures_created_at` (B-tree, DESC) - For sorting/pagination

**Triggers:**
- `update_architectures_updated_at` - Auto-updates `updated_at` on modification

---

### 2. `components`

**Purpose:** Store nodes in an architecture graph (sensors, compute nodes, control systems).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NOT NULL | auto | Primary key |
| `architecture_id` | INTEGER | NOT NULL | - | Foreign key to architectures |
| `name` | VARCHAR(255) | NOT NULL | - | Component name |
| `component_type` | VARCHAR(50) | NOT NULL | - | Type: sensor, compute, communication, control |
| `properties` | JSONB | NULL | `'{}'` | Flexible properties (CIA, criticality, etc.) |
| `position_x` | FLOAT | NULL | - | X coordinate for diagram editor |
| `position_y` | FLOAT | NULL | - | Y coordinate for diagram editor |
| `created_at` | TIMESTAMP WITH TIME ZONE | NULL | `CURRENT_TIMESTAMP` | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NULL | `CURRENT_TIMESTAMP` | Last update (auto-updated) |

**Constraints:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (architecture_id) REFERENCES architectures(id) ON DELETE CASCADE`
- `CHECK (char_length(name) > 0)`
- `CHECK (char_length(component_type) > 0)`

**Indexes:**
- `idx_components_architecture_id` (B-tree) - Fast lookup by architecture
- `idx_components_type` (B-tree) - Filter by component type
- `idx_components_created_at` (B-tree, DESC) - Sorting
- `idx_components_properties` (GIN) - JSONB queries (e.g., `WHERE properties @> '{"criticality": "HIGH"}'`)

**Triggers:**
- `update_components_updated_at` - Auto-updates `updated_at`

**Sample JSONB Properties:**
```json
{
  "confidentiality": 5,
  "integrity": 4,
  "availability": 5,
  "criticality": "HIGH",
  "vendor": "Raytheon",
  "model": "APG-81",
  "custom_field": "value"
}
```

---

### 3. `flows`

**Purpose:** Store directed edges between components (data flows, control signals).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NOT NULL | auto | Primary key |
| `architecture_id` | INTEGER | NOT NULL | - | Foreign key to architectures |
| `source_component_id` | INTEGER | NOT NULL | - | Source component (edge starts here) |
| `target_component_id` | INTEGER | NOT NULL | - | Target component (edge ends here) |
| `flow_type` | VARCHAR(50) | NULL | `'data'` | Type: data, control, power |
| `properties` | JSONB | NULL | `'{}'` | Flexible properties (bandwidth, latency, etc.) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NULL | `CURRENT_TIMESTAMP` | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NULL | `CURRENT_TIMESTAMP` | Last update (auto-updated) |

**Constraints:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (architecture_id) REFERENCES architectures(id) ON DELETE CASCADE`
- `FOREIGN KEY (source_component_id) REFERENCES components(id) ON DELETE CASCADE`
- `FOREIGN KEY (target_component_id) REFERENCES components(id) ON DELETE CASCADE`
- `CHECK (source_component_id != target_component_id)` - No self-loops
- `CHECK (char_length(flow_type) > 0)`

**Indexes:**
- `idx_flows_architecture_id` (B-tree) - Fast lookup by architecture
- `idx_flows_source_component_id` (B-tree) - Graph traversal (outgoing edges)
- `idx_flows_target_component_id` (B-tree) - Graph traversal (incoming edges)
- `idx_flows_source_target` (B-tree composite) - Fast edge lookup
- `idx_flows_type` (B-tree) - Filter by flow type
- `idx_flows_properties` (GIN) - JSONB queries

**Triggers:**
- `update_flows_updated_at` - Auto-updates `updated_at`

**Sample JSONB Properties:**
```json
{
  "bandwidth_mbps": 100,
  "latency_ms": 5,
  "protocol": "AES-256",
  "encrypted": true
}
```

---

## Cascade Delete Behavior

**Deleting an Architecture:**
```sql
DELETE FROM architectures WHERE id = 1;
```
- ✅ Cascades to all components in that architecture
- ✅ Cascades to all flows in that architecture
- Result: Clean removal with no orphaned records

**Deleting a Component:**
```sql
DELETE FROM components WHERE id = 5;
```
- ✅ Cascades to all flows where this component is source or target
- Result: Graph remains valid (no dangling edges)

---

## Performance Notes

### Index Strategy

**B-tree Indexes (12 total):**
- Primary keys (automatic)
- Foreign keys (manual for performance)
- Sorting fields (`created_at DESC`)
- Composite index on `(source_component_id, target_component_id)` for edge queries

**GIN Indexes (2 total):**
- `components.properties` - Enables fast JSONB containment queries
- `flows.properties` - Same for flow properties

### Query Performance

**Fast Queries (thanks to indexes):**
```sql
-- Get all components for architecture (uses idx_components_architecture_id)
SELECT * FROM components WHERE architecture_id = 1;

-- Get outgoing edges from component (uses idx_flows_source_component_id)
SELECT * FROM flows WHERE source_component_id = 5;

-- Find high-criticality components (uses idx_components_properties GIN)
SELECT * FROM components WHERE properties @> '{"criticality": "HIGH"}';

-- Edge existence check (uses idx_flows_source_target composite)
SELECT * FROM flows WHERE source_component_id = 2 AND target_component_id = 3;
```

**Slower Queries (full table scan):**
```sql
-- Avoid selecting all JSONB properties without filters
SELECT * FROM components WHERE properties->>'custom_field' = 'value';
-- Better: Use containment operator @>
SELECT * FROM components WHERE properties @> '{"custom_field": "value"}';
```

---

## Common Query Patterns

### 1. Get Full Architecture Graph
```sql
-- Components and flows for architecture
SELECT 
    c.id, c.name, c.component_type, c.properties,
    json_agg(json_build_object(
        'flow_id', f.id,
        'target', f.target_component_id,
        'flow_type', f.flow_type
    )) as outgoing_flows
FROM components c
LEFT JOIN flows f ON c.id = f.source_component_id
WHERE c.architecture_id = 1
GROUP BY c.id;
```

### 2. Find Critical Components
```sql
SELECT name, component_type, properties->>'criticality' as criticality
FROM components 
WHERE properties @> '{"criticality": "CRITICAL"}';
```

### 3. Graph Traversal (Successors)
```sql
-- Get all components that component 5 flows to
SELECT c.* 
FROM components c
JOIN flows f ON c.id = f.target_component_id
WHERE f.source_component_id = 5;
```

### 4. Count Components by Type
```sql
SELECT component_type, COUNT(*) as count
FROM components
GROUP BY component_type
ORDER BY count DESC;
```

---

## Schema Versioning & Migration

### Current Version: 1.0.0

**Applying Schema:**
```bash
# From project root
docker exec -i mission-db psql -U postgres -d mission_simulator < backend/schema.sql

# Or using PowerShell
Get-Content backend\schema.sql | docker exec -i mission-db psql -U postgres -d mission_simulator
```

### Future Migrations (using Alembic)

**Setup Alembic:**
```bash
cd backend
alembic init alembic
alembic revision -m "Initial schema"
alembic upgrade head
```

**Migration Strategy:**
- Use Alembic for all schema changes after Increment 1
- Keep `schema.sql` as reference/fresh install script
- Never modify existing migrations (only add new ones)

---

## Testing & Verification

### Schema Verification Commands

```sql
-- List all tables
\dt

-- Describe table structure
\d architectures
\d components
\d flows

-- List all indexes
SELECT tablename, indexname, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Check foreign keys
SELECT conname, conrelid::regclass AS "table", 
       confrelid::regclass AS "references"
FROM pg_constraint 
WHERE contype = 'f';
```

### Sample Data Script

Located at: `backend/test_data.sql`

```bash
Get-Content backend\test_data.sql | docker exec -i mission-db psql -U postgres -d mission_simulator
```

---

## Security Considerations

### Current Security Features

✅ **SQL Injection Prevention:**
- Always use parameterized queries in SQLAlchemy
- Never concatenate user input into SQL strings

✅ **Data Integrity:**
- Foreign key constraints prevent orphaned records
- Check constraints prevent invalid data (e.g., empty names)

✅ **Audit Trail:**
- `created_at` and `updated_at` on all entities
- Future: Add `user_id` for multi-tenant support

### Future Security Enhancements (Post-Increment 1)

- [ ] Add `users` table with authentication
- [ ] Add `user_id` foreign key to architectures
- [ ] Implement row-level security (RLS) for multi-tenancy
- [ ] Add soft delete (`deleted_at`) instead of hard deletes
- [ ] Add audit log table for change tracking

---

## Database Connection

### Connection String (from `.env`)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mission_simulator
```

### SQLAlchemy Usage (Python)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Usage in FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Troubleshooting

### Common Issues

**Issue: "relation does not exist"**
```bash
# Solution: Apply schema
Get-Content backend\schema.sql | docker exec -i mission-db psql -U postgres -d mission_simulator
```

**Issue: "duplicate key value violates unique constraint"**
```sql
-- Solution: Check for existing data, clear if testing
DELETE FROM architectures; -- (cascades to components and flows)
```

**Issue: "database connection refused"**
```bash
# Solution: Check Docker container is running
docker ps | grep mission-db
docker start mission-db  # if stopped
```

---

## Contact & Support

**Database Lead:** Daniel  
**Schema Version:** 1.0.0  
**Last Updated:** February 19, 2026

For schema questions or migration issues, refer to:
- [docs/SETUP.md](SETUP.md) - Setup instructions
- [backend/schema.sql](../backend/schema.sql) - Schema source
- [README.md](../README.md) - Project overview
