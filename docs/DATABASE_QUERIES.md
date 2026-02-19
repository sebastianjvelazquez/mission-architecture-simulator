# Database Viewer Options

## Quick Commands (PowerShell)

### View All Data
```powershell
# Architectures
docker exec -i mission-db psql -U postgres -d mission_simulator -c "SELECT * FROM architectures;"

# Components
docker exec -i mission-db psql -U postgres -d mission_simulator -c "SELECT id, name, component_type, properties FROM components;"

# Flows
docker exec -i mission-db psql -U postgres -d mission_simulator -c "SELECT id, source_component_id, target_component_id, flow_type FROM flows;"

# Pretty table format
docker exec -i mission-db psql -U postgres -d mission_simulator -c "\x auto" -c "SELECT * FROM components;"
```

### Interactive Shell
```powershell
# Enter PostgreSQL shell
docker exec -it mission-db psql -U postgres -d mission_simulator

# Common commands inside shell:
# \dt              - List all tables
# \d components    - Describe components table
# \q               - Quit
```

### Count Records
```powershell
docker exec -i mission-db psql -U postgres -d mission_simulator -c "SELECT 'architectures' as table, COUNT(*) FROM architectures UNION ALL SELECT 'components', COUNT(*) FROM components UNION ALL SELECT 'flows', COUNT(*) FROM flows;"
```

---

## GUI Tools (Recommended for Database Lead)

### 1. pgAdmin (PostgreSQL-specific)
**Best for:** PostgreSQL experts, deep database management

**Download:** https://www.pgadmin.org/download/

**Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `mission_simulator`
- Username: `postgres`
- Password: `postgres`

**Features:**
- Visual query builder
- Table data editor (like Excel)
- ER diagram generator
- Query history
- Export to CSV/JSON

---

### 2. DBeaver (Universal Database Tool)
**Best for:** Working with multiple databases (recommended!)

**Download:** https://dbeaver.io/download/

**Why DBeaver:**
- ✅ Works with PostgreSQL, MySQL, SQLite, everything
- ✅ Lightweight and fast
- ✅ Great SQL editor with autocomplete
- ✅ Built-in ER diagrams
- ✅ Free community edition

**Connection Details:** (same as pgAdmin)
- Driver: PostgreSQL
- Host: `localhost`
- Port: `5432`
- Database: `mission_simulator`
- Username: `postgres`
- Password: `postgres`

---

### 3. VS Code Extensions
**Best for:** Staying in your IDE

**Extensions to Install:**
1. **PostgreSQL** (by Chris Kolkman)
2. **SQLTools** (by Matheus Teixeira)
3. **SQLTools PostgreSQL/Cockroach Driver**

**Setup:**
- Install extension
- Add connection with same details as above
- Run queries directly in VS Code

---

## Sample Queries

### Get Architecture with Components
```sql
SELECT 
    a.id as arch_id,
    a.name as architecture,
    c.name as component,
    c.component_type as type,
    c.properties->>'criticality' as criticality
FROM architectures a
LEFT JOIN components c ON a.id = c.architecture_id
ORDER BY a.id, c.id;
```

### Get Component Graph (with flows)
```sql
SELECT 
    src.name as source,
    f.flow_type,
    tgt.name as target
FROM flows f
JOIN components src ON f.source_component_id = src.id
JOIN components tgt ON f.target_component_id = tgt.id
ORDER BY f.id;
```

### Count Everything
```sql
SELECT 
    'Architectures' as entity, 
    COUNT(*) as count 
FROM architectures
UNION ALL
SELECT 'Components', COUNT(*) FROM components
UNION ALL
SELECT 'Flows', COUNT(*) FROM flows;
```

---

## Clear Test Data (if needed)

```powershell
# Clear all data but keep schema
docker exec -i mission-db psql -U postgres -d mission_simulator -c "TRUNCATE TABLE architectures CASCADE;"

# Or reload schema (drops and recreates)
Get-Content backend\schema.sql | docker exec -i mission-db psql -U postgres -d mission_simulator
```
