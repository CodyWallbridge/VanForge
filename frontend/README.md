# VanForge Frontend

React and TypeScript frontend for VanForge, a WoW crafting planner
intended to maximize recipe profit within concentration budgets.

## Current status

The frontend currently displays a “VanForge Planner” heading.
The planner interface and backend integration are not implemented yet.

## Development

Run these commands from the `frontend` directory:

```powershell
npm ci
npm run dev
```

Open the local URL printed in the terminal.

## Available commands

- `npm run dev` — start the development server.
- `npm run build` — check TypeScript and build into `dist/`.
- `npm run lint` — run ESLint.
- `npm run preview` — locally preview the build after building.

## Project structure

- `src/main.tsx` — application entry point.
- `src/App.tsx` — main application component.
- `src/App.css` — application styles.
- `src/index.css` — global styles.
- `public/` — static assets.
- `vite.config.ts` — Vite configuration.
- `eslint.config.js` — lint rules.