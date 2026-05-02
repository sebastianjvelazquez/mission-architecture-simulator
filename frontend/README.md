# Frontend

Next.js application for building, saving, loading, and simulating mission architectures.

The frontend provides the interactive diagram editor, saved architecture controls, simulation modal, and dashboard views for mission impact analysis.

## Stack

- Next.js
- React
- TypeScript
- React Flow
- Recharts
- Tailwind CSS

## Run Locally

```bash
cd frontend
npm install
npm run dev
```

Default local frontend URL:

```text
http://localhost:3000
```

## Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, this points to the Render backend:

```bash
NEXT_PUBLIC_API_URL=https://mission-architecture-simulator.onrender.com
```

## Checks

```bash
npm run lint
npm run build
npm test
```
