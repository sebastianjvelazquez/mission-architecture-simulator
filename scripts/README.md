# Scripts

Utility scripts for development and deployment.

## Available Scripts

| Script | Purpose |
|---|---|
| `lint.sh` | Run linting checks |
| `test.sh` | Run the test suite |
| `test_demo.sh` | Run a demo test against a live backend |
| `view_database.ps1` | Inspect the local PostgreSQL database |

## Applying the Schema

### Local development

```bash
psql postgresql://postgres:postgres@localhost:5432/mission_simulator -f backend/schema.sql
```

### Production (Render)

Use the External Database URL from the Render dashboard (temporary access):

```bash
psql "$EXTERNAL_DATABASE_URL" -f backend/schema.sql
```

See [docs/production-database.md](../docs/production-database.md) for the full provisioning guide.

## Seeding Demo Data

```bash
# Local
psql postgresql://postgres:postgres@localhost:5432/mission_simulator -f backend/test_data.sql

# Production
psql "$EXTERNAL_DATABASE_URL" -f backend/test_data.sql
```
