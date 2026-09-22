# VanForge Frontend

React and TypeScript frontend for the VanForge crafting planner.

## Configuration

Create `frontend/.env.local` with the Neon Auth URL:

```dotenv
VITE_NEON_AUTH_URL=https://your-neon-auth-host
```

Local API requests use the `/api` Vite proxy configured in `vite.config.ts`.

## Development

Run these commands from the `frontend` directory:

```powershell
npm ci
npm run dev
```

Open the local URL printed in the terminal. The backend must also be running.

## Available commands

- `npm run dev` starts the development server.
- `npm run build` checks TypeScript and creates the production build.
- `npm run lint` runs ESLint.
- `npm run preview` previews the production build locally.

## Application structure

- `src/api/` contains typed backend request functions.
- `src/components/` contains reusable interface components.
- `src/dto/` contains frontend representations of API request and response DTOs.
- `src/pages/` contains routed pages and their styles.
- `src/auth.ts` configures the Neon Auth clients.
- `src/App.tsx` handles authentication, account loading, authorization-aware routes, and layout.

Authenticated users can manage their characters, selected expansion, known recipes, concentration costs, and account-specific recipe profits. Administrators can also manage shared expansions, recipes, ingredients, and local account roles.
