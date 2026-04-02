# Increment 2 Demo Video Script

## Goal

Record a 5-7 minute demo of the live Increment 2 deployment for the
Mission-System Security Architecture Simulator.

- Frontend: `https://mission-architecture-simulator.vercel.app`
- Backend API: `https://mission-architecture-simulator.onrender.com`
- API Docs: `https://mission-architecture-simulator.onrender.com/docs`

## Before Recording

1. Open the Vercel frontend in a browser.
2. If the first API request is slow, wait for the Render free-tier backend to wake up.
3. Make sure Render `ALLOWED_ORIGINS` includes:

```text
https://mission-architecture-simulator.vercel.app,http://localhost:3000
```

4. Have one saved architecture ready for the demo.
5. Close unrelated tabs and turn on Do Not Disturb.

## Script

### 0:00-0:30 Opening

"This is Group 4's Increment 2 demo for the Mission-System Security
Architecture Simulator. We are showing the live deployed application, not a
localhost build. The frontend is hosted on Vercel, and the backend API is
hosted on Render."

Action:
- Show the Vercel URL in the browser.
- Briefly show the homepage/editor.

### 0:30-1:30 Save and Load

"The editor lets a mission planner build an architecture visually and persist
it to the backend database."

Action:
- Show the architecture on the canvas.
- Click Save and confirm the success message.
- Open Load and show the saved architecture list.
- Reload the saved architecture.

### 1:30-2:45 Run a Simulation

"Increment 2 connects the frontend to the backend simulation API. We can now
run a mission-impact simulation from the interface."

Action:
- Open Run Simulation.
- Select a scenario and a target component.
- Submit the simulation.
- Transition to the dashboard/results view.

### 2:45-4:15 Dashboard Results

"The dashboard now shows real simulation data rather than placeholder values."

Action:
- Point out the baseline score.
- Point out the compromised score and delta.
- Show the affected components and unaffected components.
- Highlight the attack path or explanation text if present.

### 4:15-5:15 Deployment and API

"For deployment, the frontend is live on Vercel and the backend plus PostgreSQL
are running on Render. The backend health check and API docs are publicly
available."

Action:
- Open `https://mission-architecture-simulator.onrender.com/health`
- Open `https://mission-architecture-simulator.onrender.com/docs`
- Briefly show that the API is live.

### 5:15-6:15 Testing and CI

"On the quality side, Increment 2 includes expanded integration testing,
coverage enforcement in CI, and updated documentation."

Action:
- Mention the integration tests.
- Mention the coverage threshold in GitHub Actions.
- Mention the updated RD v2, IT v2, and setup documentation.

### 6:15-7:00 Closing

"That completes the Increment 2 demo. The project now supports live frontend to
backend integration, public deployment, and updated testing and documentation.
Thank you for watching."

Action:
- End on the live frontend URL or GitHub repo page.

## Recording Checklist

- Show the live Vercel URL at least once.
- Show the Render health or docs page at least once.
- Demonstrate save, load, and simulation.
- Keep the demo between 5 and 7 minutes.
- Upload to YouTube and replace the placeholder link in `docs/Progress_Report_2.md`.
