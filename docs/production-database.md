# Production Database — Render PostgreSQL

## Overview

This project uses a PostgreSQL 15 instance hosted on Render's free tier for production.

> **Warning:** Render's free PostgreSQL tier expires after **90 days** from creation. The database and all its data will be deleted automatically. Plan to recreate and reseed the instance before expiry if the project is still active.

---

## Provisioning Steps (One-Time Setup)

### 1. Create the PostgreSQL Instance on Render

1. Log in to [render.com](https://render.com) and go to the dashboard.
2. Click **New +** → **PostgreSQL**.
3. Configure the instance:
   - **Name:** `mission-simulator-db`
   - **Database:** `mission_simulator`
   - **User:** `mission_user` (Render generates a password automatically)
   - **Region:** Match the region of the backend web service (e.g. `US East (Ohio)`)
   - **PostgreSQL Version:** 18
   - **Plan:** Free
4. Click **Create Database** and wait for the instance to become available (~1–2 min).

### 2. Retrieve the Connection Strings

From the Render database dashboard, find two URLs:

| URL Type | When to Use |
|---|---|
| **Internal Database URL** | Set as `DATABASE_URL` in the Render **backend web service** env vars. Traffic stays within Render's private network — faster and free. |
| **External Database URL** | Use temporarily from your local machine to run `psql` and apply the schema (step 3 below). |

> **Security note:** Never commit either URL to the repository. Share via a secure channel (e.g. private Slack DM or Render's shared environment group).

### 3. Apply the Schema

Run from your local machine using the **External Database URL**:

```bash
psql "$EXTERNAL_DATABASE_URL" -f backend/schema.sql
```

The schema creates all six tables (`architectures`, `components`, `flows`, `mitigations`, `scenarios`, `simulation_results`) plus indexes and auto-update triggers.

### 4. Seed Demo Data (Optional)

```bash
psql "$EXTERNAL_DATABASE_URL" -f backend/test_data.sql
```

This inserts a sample UAV Surveillance System architecture with components and flows for demo purposes.

### 5. Configure Environment Variables on Render

In the Render dashboard for the **backend web service**, add:

| Key | Value |
|---|---|
| `DATABASE_URL` | The **Internal Database URL** from step 2 |
| `ENVIRONMENT` | `production` |
| `ALLOWED_ORIGINS` | The deployed frontend URL (e.g. `https://your-frontend.onrender.com`) |

The `DATABASE_URL` is what limits database access to the Render backend service only — the internal hostname is not routable from the public internet.

---

## Verifying the Connection

After deploying the backend service, hit the DB health endpoint:

```bash
curl https://your-api.onrender.com/health/db
```

Expected response (HTTP 200):
```json
{"status": "connected", "environment": "production"}
```

If you get HTTP 503, check:
1. `DATABASE_URL` is set to the **Internal** URL in the backend service env vars.
2. Both the DB instance and the web service are in the same Render region.
3. The backend service has finished deploying (check Render logs).

---

## Security Notes

- The Internal Database URL is never routable from outside Render — no firewall rules needed.
- The External Database URL should only be used temporarily for schema migrations; rotate or note its expiry.
- Neither URL should ever be committed to the repository (`.env` is gitignored; `.env.example` contains only placeholders).
- Share the `DATABASE_URL` with team members (Person 2, Person 4) via a private channel, not GitHub comments or PR descriptions.

---

## 90-Day Expiry Reminder

Render free PostgreSQL instances are deleted **90 days after creation**. Before expiry:

1. Export any data you want to keep: `pg_dump "$EXTERNAL_DATABASE_URL" > backup.sql`
2. Create a new free PostgreSQL instance following this guide.
3. Apply the schema and reseed.
4. Update `DATABASE_URL` in the backend service env vars.
