# Deployment Guide

## Mission-System Security Architecture Simulator

**Group 4 — Increment 3**

---

This guide covers deploying the application to production:
- **Frontend** → Vercel
- **Backend API** → Render (Web Service)
- **Database** → Render (Managed PostgreSQL)

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Deploy PostgreSQL Database on Render](#2-deploy-postgresql-database-on-render)
3. [Deploy Backend API on Render](#3-deploy-backend-api-on-render)
4. [Deploy Frontend on Vercel](#4-deploy-frontend-on-vercel)
5. [Connect the Services](#5-connect-the-services)
6. [Verify the Deployment](#6-verify-the-deployment)
7. [End-to-End Test Checklist (Issue #96)](#7-end-to-end-test-checklist-issue-96)
8. [Troubleshooting](#8-troubleshooting)
9. [Final Submission Checklist (Issue #98)](#9-final-submission-checklist-issue-98)

---

## 1. Prerequisites

- GitHub repository: `https://github.com/sebastianjvelazquez/mission-architecture-simulator`
- A Render account (free): https://render.com
- A Vercel account (free): https://vercel.com
- Admin access to the GitHub repository (to configure deployment secrets)

---

## 2. Deploy PostgreSQL Database on Render

### Step 1: Create a new PostgreSQL instance

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **PostgreSQL**
3. Fill in the form:
   - **Name:** `mission-simulator-db`
   - **Database:** `mission_simulator`
   - **User:** `mission_user` (Render may auto-generate this)
   - **Region:** Choose the closest to your users (e.g. US East)
   - **Plan:** Free
4. Click **Create Database**
5. Wait for the database to become **Available** (1-2 minutes)

### Step 2: Note the connection strings

After creation, open the database page and note:
- **Internal Database URL** — used by the backend service (same Render region, no SSL needed)
- **External Database URL** — used if you need to connect from your local machine

Example format:
```
postgresql://mission_user:<password>@<host>.render.com/mission_simulator
```

### Step 3: Apply the schema

Connect via the External URL from your local machine:
```bash
psql "<external_database_url>" -f backend/schema.sql
```

Optionally load seed data:
```bash
psql "<external_database_url>" -f backend/test_data.sql
```

---

## 3. Deploy Backend API on Render

### Step 1: Create a new Web Service

1. From the Render Dashboard, click **New** → **Web Service**
2. Click **Connect a repository** and select `mission-architecture-simulator`
3. Configure the service:
   - **Name:** `mission-simulator-api`
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:**
     ```
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan:** Free

### Step 2: Add environment variables

In the **Environment** section of the Web Service settings, add:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Internal Database URL from Step 2.2 |
| `FRONTEND_URL` | `https://<your-app>.vercel.app` (get this after deploying frontend) |
| `ENVIRONMENT` | `production` |

> **Note:** You can set `FRONTEND_URL` to `*` temporarily during setup, then update it once
> the Vercel URL is known. This controls the CORS allowed origins.

### Step 3: Deploy

Click **Create Web Service**. Render will:
1. Clone the `main` branch
2. Run `pip install -r requirements.txt`
3. Start the server with `uvicorn`

The first deploy takes 2-5 minutes. Subsequent deploys triggered by `git push` to `main`
are faster.

### Step 4: Note the backend URL

After deployment, Render shows a URL like:
```
https://mission-simulator-api.onrender.com
```

Test it:
```bash
curl https://mission-simulator-api.onrender.com/health
# Expected: {"status": "healthy"}
```

> **Free tier note:** Render's free tier spins down instances after 15 minutes of
> inactivity. The first request after idle may take 20-30 seconds (cold start).

---

## 4. Deploy Frontend on Vercel

### Step 1: Import the GitHub repository

1. Log in to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New…** → **Project**
3. Import `sebastianjvelazquez/mission-architecture-simulator`
4. Configure the project:
   - **Framework Preset:** Next.js (auto-detected)
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)

### Step 2: Add environment variables

Under **Environment Variables**, add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://mission-simulator-api.onrender.com` |

> The `NEXT_PUBLIC_` prefix makes this variable available in client-side code.

### Step 3: Deploy

Click **Deploy**. Vercel will:
1. Clone the repository
2. Run `npm install`
3. Run `npm run build`
4. Deploy to its global CDN

After deployment (1-3 minutes), Vercel provides a URL like:
```
https://mission-architecture-simulator.vercel.app
```

### Step 4: Update CORS on the backend

Now that you have the Vercel URL, go back to Render → your Web Service → **Environment**
and update `FRONTEND_URL` to the exact Vercel URL:
```
FRONTEND_URL=https://mission-architecture-simulator.vercel.app
```

Click **Save Changes** to trigger a redeploy.

---

## 5. Connect the Services

After both services are deployed:

1. **Backend CORS** must allow the Vercel domain. Verify by checking `app/core/config.py`
   reads `FRONTEND_URL` as an allowed origin.

2. **Frontend API base URL** must point to the Render backend. Verify by checking
   `NEXT_PUBLIC_API_URL` is set in Vercel environment variables.

3. **Database connection**: The backend reads `DATABASE_URL` from the environment. On
   Render, this is set to the Internal Database URL which is accessible only within
   Render's network (fast, no SSL overhead).

---

## 6. Verify the Deployment

### Backend health check
```bash
curl https://mission-simulator-api.onrender.com/health
```
Expected:
```json
{"status": "healthy"}
```

### API documentation
Open in browser:
```
https://mission-simulator-api.onrender.com/docs
```

### Create a test architecture via API
```bash
curl -X POST https://mission-simulator-api.onrender.com/architectures \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Arch",
    "components": [
      {"component_id": "s1", "name": "Sensor", "component_type": "Sensor"}
    ],
    "flows": []
  }'
```
Expected: `201 Created` with the architecture JSON.

### Frontend
Open `https://mission-architecture-simulator.vercel.app` in a browser and verify:
- The page loads without errors
- The architecture editor canvas is visible
- Creating and saving an architecture works

---

## 7. End-to-End Test Checklist (Issue #96)

Use this checklist to verify the live deployment works end-to-end.

### Architecture Management

- [ ] **Create architecture**: Add at least 3 components (Sensor, Compute, Control) via
      the drag-and-drop editor. Click Save. Verify it appears in the architecture list.
- [ ] **Load architecture**: Refresh the page, select the saved architecture from the
      list, verify all components and flows are restored.
- [ ] **Edit component**: Click a component, change its name or criticality, save.
      Reload and verify the change persisted.
- [ ] **Delete component**: Delete a component from the canvas. Verify its flows are
      also removed.
- [ ] **Delete architecture**: Delete the entire architecture. Verify it no longer
      appears in the list.

### Simulation

- [ ] **Run node_compromise**: Select a saved architecture with at least 3 connected
      components. Pick the Sensor as the target. Run simulation. Verify:
  - Baseline score is shown (typically 100%)
  - Compromised score is lower than baseline
  - Affected components list includes the Sensor and its downstream components
  - Attack path is shown step-by-step
  - Bar chart compares baseline vs compromised
- [ ] **Invalid target**: Try to simulate with a component that has no connections.
      Verify the response still makes sense.

### Scenario Persistence

- [ ] **Save scenario**: After running a simulation, save the scenario with a name.
      Verify a 201 response with the scenario details.
- [ ] **List scenarios**: Call `GET /architectures/{id}/scenarios`. Verify the saved
      scenario appears.
- [ ] **Delete scenario**: Delete the scenario. Verify 204 response and it's gone from
      the list.

### Error Handling

- [ ] **404 on invalid ID**: Call `GET /architectures/99999`. Verify 404 response.
- [ ] **422 on invalid input**: Call `POST /architectures` with `"name": ""`.
      Verify 422 response.
- [ ] **CORS**: Open browser DevTools → Network tab. Verify API calls from the Vercel
      frontend include `Access-Control-Allow-Origin` in the response headers.

### API Documentation

- [ ] **Swagger UI**: Open `/docs` on the backend URL. Verify all endpoints are listed
      with their schemas.

---

## 8. Troubleshooting

### Backend cold start (30-second delay on first request)

**Cause:** Render free tier spins down idle services.
**Fix:** The first request will be slow. Subsequent requests are fast. Consider using a
cron job or UptimeRobot to ping `/health` every 10 minutes to keep the service warm.

### CORS errors in browser

**Symptom:** Browser shows `Access to fetch at '...' from origin '...' has been blocked
by CORS policy.`
**Fix:** Ensure `FRONTEND_URL` on the Render backend exactly matches the Vercel URL
(including `https://` and no trailing slash). Trigger a Render redeploy after changing.

### Database connection error on Render

**Symptom:** Backend returns 500 errors, Render logs show `sqlalchemy.exc.OperationalError`.
**Fix:**
1. Verify `DATABASE_URL` is set to the **Internal** (not External) Database URL on Render.
2. Verify the database status is **Available** on Render Dashboard.
3. Re-apply the schema: `psql "<external_url>" -f backend/schema.sql`.

### Next.js build fails on Vercel

**Symptom:** Vercel deployment shows build errors.
**Fix:**
1. Verify `NEXT_PUBLIC_API_URL` is set in Vercel environment variables.
2. Run `cd frontend && npm run build` locally to reproduce the error.
3. Check `next.config.ts` for any environment-specific settings.

### Tests fail locally

**Symptom:** `pytest tests/` fails.
**Fix:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ --cov=app
```
Ensure you have Python 3.11+ installed. SQLite is used for tests — no PostgreSQL needed.

---

## 9. Final Submission Checklist (Issue #98)

Use this checklist before submitting on Canvas.

### Code

- [ ] All Increment 3 feature branches merged to `Increment3`
- [ ] `Increment3` branch merged to `main`
- [ ] CI pipeline green on `main` branch
- [ ] Coverage ≥ 85% (currently 94.24%)
- [ ] No uncommitted changes

### Documentation

- [ ] `docs/RD_v3.md` — Requirements Document v3
- [ ] `docs/IT_v3.md` — Implementation & Testing Document v3
- [ ] `docs/TRACEABILITY.md` — Traceability Matrix
- [ ] `docs/Progress_Report_3.md` — Progress Report Increment 3
- [ ] `docs/DEPLOYMENT.md` — This deployment guide
- [ ] `README.md` — Updated with live URLs

### Deployment

- [ ] Frontend live at Vercel URL (test in browser)
- [ ] Backend live at Render URL (test `/health` endpoint)
- [ ] Database schema applied on Render PostgreSQL

### Demo Video

- [ ] Screen recording showing the live application
- [ ] Covers: create arch → draw flows → save → run simulation → view results
- [ ] Shows live deployment URL in browser address bar
- [ ] Video uploaded to YouTube/Drive (unlisted) or Canvas
- [ ] Video link added to `docs/Progress_Report_3.md`

### Canvas Submission

- [ ] GitHub repository URL submitted
- [ ] Vercel frontend URL submitted
- [ ] Render backend URL submitted
- [ ] Demo video link submitted
- [ ] All team member FSU IDs confirmed in submission
