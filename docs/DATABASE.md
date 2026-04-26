# Database Design Documentation

Schema Version: 3.0.0 (Increment 3)
PostgreSQL Version: 15+
ORM: SQLAlchemy 2.0 (DeclarativeBase)
Last Updated: April 26, 2026
Owner: Person 3 (Database and Integration Lead)

---

## Overview

The production schema now contains six tables:

1. architectures
2. components
3. flows
4. mitigations
5. scenarios
6. simulation_results

All core foreign-key chains are in place with delete behaviors designed to prevent orphaned rows.

---

## Table Schemas

### architectures

Purpose: top-level mission architecture record and clone lineage root.

| Column | Type | Null | Default | Notes |
|---|---|---|---|---|
| id | SERIAL | no | auto | Primary key |
| name | VARCHAR(255) | no | - | Required architecture name |
| description | TEXT | yes | - | Optional |
| is_clone | BOOLEAN | no | false | True for cloned records |
| parent_id | INTEGER | yes | - | FK to architectures.id, ON DELETE SET NULL |
| properties | JSONB | yes | '{}'::jsonb | Arbitrary metadata |
| created_at | TIMESTAMPTZ | yes | CURRENT_TIMESTAMP | Audit timestamp |
| updated_at | TIMESTAMPTZ | yes | CURRENT_TIMESTAMP | Updated by trigger |

Constraints:

- PRIMARY KEY (id)
- CHECK name_not_empty
- FK parent_id -> architectures.id ON DELETE SET NULL

### components

Purpose: architecture nodes.

| Column | Type | Null | Default | Notes |
|---|---|---|---|---|
| id | SERIAL | no | auto | Primary key |
| architecture_id | INTEGER | no | - | FK to architectures.id ON DELETE CASCADE |
| component_id | VARCHAR(255) | yes | - | Frontend stable ID/slug |
| name | VARCHAR(255) | no | - | Required |
| component_type | VARCHAR(50) | no | - | Required type |
| criticality | INTEGER | no | 5 | App-level validation is 1..10 |
| properties | JSONB | yes | '{}'::jsonb | Extra metadata |
| position_x | FLOAT | yes | - | Diagram coordinate |
| position_y | FLOAT | yes | - | Diagram coordinate |
| created_at | TIMESTAMPTZ | yes | CURRENT_TIMESTAMP | Audit timestamp |
| updated_at | TIMESTAMPTZ | yes | CURRENT_TIMESTAMP | Updated by trigger |

Constraints:

- PRIMARY KEY (id)
- CHECK name_not_empty
- CHECK valid_component_type
- FK architecture_id -> architectures.id ON DELETE CASCADE

### flows

Purpose: directed edges between components.

| Column | Type | Null | Default | Notes |
|---|---|---|---|---|
| id | SERIAL | no | auto | Primary key |
| architecture_id | INTEGER | no | - | FK to architectures.id ON DELETE CASCADE |
| source_component_id | INTEGER | no | - | FK to components.id ON DELETE CASCADE |
| target_component_id | INTEGER | no | - | FK to components.id ON DELETE CASCADE |
| data_type | VARCHAR(100) | yes | - | Example: telemetry, commands |
| cia_requirement | VARCHAR(50) | yes | - | confidentiality/integrity/availability |
| latency_sensitivity | VARCHAR(20) | yes | - | low/medium/high |
| properties | JSONB | yes | '{}'::jsonb | Edge metadata |
| created_at | TIMESTAMPTZ | yes | CURRENT_TIMESTAMP | Audit timestamp |
| updated_at | TIMESTAMPTZ | yes | CURRENT_TIMESTAMP | Updated by trigger |

Constraints:

- PRIMARY KEY (id)
- CHECK no_self_loops
- FK architecture_id -> architectures.id ON DELETE CASCADE
- FK source_component_id -> components.id ON DELETE CASCADE
- FK target_component_id -> components.id ON DELETE CASCADE

### mitigations

Purpose: persisted mitigation recommendations tied to an architecture.

| Column | Type | Null | Default | Notes |
|---|---|---|---|---|
| id | SERIAL | no | auto | Primary key |
| architecture_id | INTEGER | no | - | FK to architectures.id ON DELETE CASCADE |
| type | VARCHAR(100) | no | - | Mitigation category |
| affected_component_id | INTEGER | yes | - | FK to components.id ON DELETE SET NULL |
| description | TEXT | no | - | Human-readable guidance |
| created_at | TIMESTAMPTZ | yes | CURRENT_TIMESTAMP | Audit timestamp |

Constraints:

- PRIMARY KEY (id)
- FK architecture_id -> architectures.id ON DELETE CASCADE
- FK affected_component_id -> components.id ON DELETE SET NULL

### scenarios

Purpose: saved simulation scenario definitions.

| Column | Type | Null | Default | Notes |
|---|---|---|---|---|
| id | SERIAL | no | auto | Primary key |
| architecture_id | INTEGER | no | - | FK to architectures.id ON DELETE CASCADE |
| scenario_type | VARCHAR(100) | no | - | Scenario discriminator |
| target_component_id | INTEGER | no | - | FK to components.id ON DELETE CASCADE |
| parameters | JSONB | yes | '{}'::jsonb | Scenario config payload |
| created_at | TIMESTAMPTZ | yes | CURRENT_TIMESTAMP | Audit timestamp |

### simulation_results

Purpose: persisted outputs for scenario runs.

| Column | Type | Null | Default | Notes |
|---|---|---|---|---|
| id | SERIAL | no | auto | Primary key |
| scenario_id | INTEGER | no | - | FK to scenarios.id ON DELETE CASCADE |
| baseline_score | FLOAT | no | - | Pre-attack score |
| compromised_score | FLOAT | no | - | Post-attack score |
| affected_components | JSONB | yes | '[]'::jsonb | Component IDs |
| attack_path | JSONB | yes | '[]'::jsonb | Step list |
| explanation | TEXT | yes | - | Human-readable summary |
| created_at | TIMESTAMPTZ | yes | CURRENT_TIMESTAMP | Audit timestamp |

---

## Index Review

Indexes currently in backend/schema.sql:

- architectures: idx_architectures_name, idx_architectures_created_at, idx_architectures_parent_id
- components: idx_components_architecture_id, idx_components_component_id, idx_components_type, idx_components_created_at, idx_components_properties (GIN)
- flows: idx_flows_architecture_id, idx_flows_source_component_id, idx_flows_target_component_id, idx_flows_source_target, idx_flows_properties (GIN)
- mitigations: idx_mitigations_architecture_id, idx_mitigations_type, idx_mitigations_affected_component_id
- scenarios: idx_scenarios_architecture_id, idx_scenarios_scenario_type, idx_scenarios_target_component_id, idx_scenarios_created_at, idx_scenarios_parameters (GIN)
- simulation_results: idx_simulation_results_scenario_id, idx_simulation_results_created_at, idx_simulation_results_affected_components (GIN), idx_simulation_results_attack_path (GIN)

Required frequently queried columns are indexed:

- architecture_id is indexed in components, flows, mitigations, and scenarios
- component_id is indexed in components via idx_components_component_id

---

## Foreign Keys and Delete Behavior Verification

Verified FK rules and expected behavior:

1. architectures -> components, flows, mitigations, scenarios use ON DELETE CASCADE through child FKs.
2. scenarios -> simulation_results uses ON DELETE CASCADE.
3. flows source_component_id and target_component_id use ON DELETE CASCADE.
4. architecture parent_id uses ON DELETE SET NULL (intentional for clone lineage).
5. mitigations affected_component_id uses ON DELETE SET NULL (keep mitigation text even if component deleted).

Practical cascade outcome:

- Deleting an architecture removes all of its components, flows, mitigations, scenarios, and scenario results.

Validation query:

```sql
SELECT conname,
       conrelid::regclass AS child_table,
       confrelid::regclass AS parent_table,
       pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE contype = 'f'
ORDER BY conrelid::regclass::text, conname;
```

---

## Backup and Recovery Strategy (Render PostgreSQL)

### Free Tier Constraint

Render PostgreSQL free tier has a 1 GB storage limit. This must be monitored to avoid write failures and backup truncation risk.
Render free PostgreSQL instances also expire after 90 days, so scheduled backup and restore drills are required.

### Backup

Preferred: pg_dump custom format.

```bash
pg_dump "$DATABASE_URL" --format=custom --compress=9 --file=mission_backup.dump
```

Alternative (plain SQL):

```bash
pg_dump "$DATABASE_URL" --format=plain > mission_backup.sql
```

### Restore

Custom dump restore:

```bash
pg_restore --clean --if-exists --no-owner --no-privileges \
  --dbname "$DATABASE_URL" mission_backup.dump
```

Plain SQL restore:

```bash
psql "$DATABASE_URL" -f mission_backup.sql
```

### Operational Cadence

- Development/staging: backup at least before schema changes and destructive tests.
- Production: daily backup plus a pre-release backup before each deployment.
- Keep at least 7 rolling backups in secure storage.

---

## Production Readiness Checklist

1. schema.sql reflects Increment 3 entities and clone metadata.
2. FK behavior reviewed and documented.
3. High-value indexes confirmed, including architecture_id and component_id.
4. Render backup and restore workflow documented.
5. Production DATABASE_URL format documented in setup docs.

---

## Troubleshooting Quick Notes

- relation does not exist: ensure init_db() has run or apply schema.sql.
- connection refused: verify Render DB is reachable and DATABASE_URL is correct.
- slow queries: run EXPLAIN ANALYZE and check missing/unused indexes.
- storage pressure near 1 GB on Render free tier: archive old records and rotate backups.
