# Progress Report — Increment 3

## Mission-System Security Architecture Simulator

**Group 4**

**Date:** April 27, 2026

**Course:** CEN 4090L — Software Engineering Lab

---

## 1. Increment 3 Overview

Increment 3 is the final increment of the Mission-System Security Architecture Simulator.
The primary goals were:

1. **Complete Increment 3 features** — scenario comparison, architecture cloning,
   mitigation suggestions
2. **Deploy to production** — Vercel (frontend) + Render (backend + PostgreSQL)
3. **Achieve 85%+ test coverage** — target was 85%, achieved **94.24%**
4. **Finalize all documentation** — RD v3, IT v3, Traceability Matrix, Deployment Guide
5. **Create demo video** — recording of the live deployed application

---

## 2. What Was Completed in Increment 3

### Testing & DevOps (Sebastian Velazquez — sv24m)

| Task | Issue | Status |
|------|-------|--------|
| Add tests for mitigation/clone/compare logic (xfail placeholders + error coverage) | #90 | ✅ Done |
| Achieve 85%+ test coverage | #92 | ✅ **94.24% achieved** |
| Traceability Matrix | #91 | ✅ Done (`docs/TRACEABILITY.md`) |
| Requirements Document v3 | #93 | ✅ Done (`docs/RD_v3.md`) |
| Implementation & Testing Document v3 | #94 | ✅ Done (`docs/IT_v3.md`) |
| Deploy Frontend to Vercel | #95 | 🔄 In Progress |
| End-to-End Testing on Live Deployment | #96 | 🔄 Pending live deployment |
| Demo Video & Progress Report Increment 3 | #97 | ✅ Done |
| Final Deliverables Submission | #98 | 🔄 Pending Canvas submission |

### Backend (William Ohonba — weo24)

| Task | Issue | Status |
|------|-------|--------|
| Mitigation Suggester Logic & Clone Endpoint | #83 | 🔄 In Progress |
| Compare Scenarios & Mitigation Scoring | #84 | 🔄 In Progress |
| Backend deployed to Render | #86 | 🔄 In Progress |

### Frontend (Samson Shields — sjs23g)

| Task | Issue | Status |
|------|-------|--------|
| Architecture Editor Enhancements | #81 | 🔄 In Progress |
| Mitigation UI Panel | #82 | 🔄 In Progress |
| Scenario Replay UI | #85 | 🔄 In Progress |

### Database (Daniel Gonzalez — dg23c)

| Task | Issue | Status |
|------|-------|--------|
| Database Query Optimization | #87 | 🔄 In Progress |
| Seed data for demo | #88 | 🔄 In Progress |

---

## 3. Test Coverage Progress

| Increment | Test Count | Coverage |
|-----------|-----------|---------|
| Increment 1 | 157 | 94.81% |
| Increment 2 | 187 | 90.31% |
| **Increment 3** | **221** | **94.24%** |

The new `tests/test_increment3.py` file added 34 tests covering previously unreached
error paths in `architectures.py` and `scenarios.py`, plus simulator edge cases. The
9 xfail placeholder tests for clone/mitigation/compare are included and will be converted
to real tests when Person 2 merges those endpoints.

**Remaining uncovered lines:**
- `app/database.py` lines 37-47: SQLAlchemy slow-query event listeners (require real
  PostgreSQL + `ENVIRONMENT=production` env var; not testable with SQLite)
- `app/api/scenarios.py` lines 281-313: CSV export and some pagination paths

---

## 4. Lessons Learned

### What Worked Well

- **SQLite in-memory testing pattern**: Using SQLite with `StaticPool` and patching
  `SQLiteTypeCompiler.visit_JSONB = SQLiteTypeCompiler.visit_JSON` allowed full DB
  integration tests without needing a live PostgreSQL instance.
- **xfail placeholders**: Marking future feature tests as `xfail(strict=False)` let
  us commit the tests before the endpoints existed, keeping CI green while documenting
  the expected behavior.
- **Mock-based error testing**: Using `MagicMock(spec=Session)` with `side_effect`
  for targeted flush/commit failures was more reliable than trying to trigger real
  database errors in the test environment.
- **Feature branch strategy**: One branch per issue kept PRs small and focused.

### What Could Improve

- **Test isolation**: Some module-scoped fixtures meant test order affected results.
  Function-scoped fixtures would be more robust.
- **Frontend E2E tests**: We relied on manual E2E testing. Playwright or Cypress would
  automate this for future increments.
- **Environment parity**: The Python version difference between Docker (3.11) and local
  (3.14) caused occasional compatibility warnings. Pinning the local venv to 3.11 would
  eliminate this.
- **Earlier CI for frontend**: The frontend had no automated tests in CI. Adding a
  Next.js build check (`npm run build`) to the CI pipeline would catch regressions early.

---

## 5. Team Contributions Summary

| Team Member | Role | Increment 3 Contributions |
|-------------|------|--------------------------|
| Samson Shields (sjs23g) | Frontend Lead | Architecture editor UI, scenario replay panel, mitigation UI |
| William Ohonba (weo24) | Backend Lead | Clone endpoint, mitigation suggester, compare endpoint, Render deployment |
| Daniel Gonzalez (dg23c) | Database Lead | Query optimization, demo seed data |
| Sebastian Velazquez (sv24m) | DevOps/Testing Lead | 94.24% coverage, 221 tests, RD v3, IT v3, Traceability Matrix, Deployment Guide, CI/CD |

---

## 6. Live Deployment URLs

> **Note:** URLs will be added once deployments are complete.

| Component | URL |
|-----------|-----|
| Frontend (Vercel) | _TBD — see Issue #95_ |
| Backend API (Render) | _TBD — see Issue #86_ |
| API Docs (Swagger) | `<backend_url>/docs` |

---

## 7. Demo Video

**Demo Video Link:** [https://youtu.be/gMlu0X0HnO0](https://youtu.be/gMlu0X0HnO0)

**Planned demo flow:**
1. Show live frontend URL in browser
2. Create a new architecture by adding components (Sensor, Compute, Control)
3. Draw flows between components
4. Save the architecture
5. Run a node_compromise simulation on the Sensor component
6. Show the bar chart and affected components list
7. Save the scenario for replay
8. (If merged) Show clone architecture
9. (If merged) Show mitigation suggestions
10. Show API Swagger docs at `/docs`
11. Show GitHub Actions CI run (green)
12. Show test coverage output: 94.24%

---

## 8. Appendix — Increment 3 GitHub Issues

| Issue # | Title | Assignee |
|---------|-------|----------|
| #80 | Frontend Architecture Editor Enhancements | @samsonshields |
| #81 | Mitigation Suggestion UI Panel | @samsonshields |
| #82 | Scenario Replay UI | @samsonshields |
| #83 | Mitigation Suggester Logic & Clone Endpoint | @William-Ohonba |
| #84 | Compare Scenarios & Mitigation Scoring Logic | @William-Ohonba |
| #85 | Advanced Scenario Replay API Endpoint | @William-Ohonba |
| #86 | Deploy Backend to Render | @William-Ohonba |
| #87 | Database Query Optimization | @dgonz10663 |
| #88 | Seed Data for Demo | @dgonz10663 |
| #89 | Database Schema for Scenarios | @dgonz10663 |
| #90 | Tests for Mitigation & Clone/Compare Logic | @sebastianjvelazquez |
| #91 | Traceability Matrix & Deployment Architecture Plan | @sebastianjvelazquez |
| #92 | Achieve 85%+ Test Coverage | @sebastianjvelazquez |
| #93 | Requirements Document (RD) v3 | @sebastianjvelazquez |
| #94 | Implementation & Testing Document (IT) v3 | @sebastianjvelazquez |
| #95 | Deploy Frontend to Vercel | @sebastianjvelazquez |
| #96 | End-to-End Testing on Live Deployment | @sebastianjvelazquez |
| #97 | Final Demo Video & Progress Report Increment 3 | @sebastianjvelazquez |
| #98 | Final Deliverables Submission Increment 3 | @sebastianjvelazquez |
