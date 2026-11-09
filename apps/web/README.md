# PUSTORA web application

The web app is a responsive React + TypeScript client built with Vite. Its current scope is the public PUSTORA landing shell, route-level loading/error handling, and a not-found route; it does not yet implement catalog, identity, checkout, or staff workflows.

## Requirements and setup

- Node.js `26.13.0` is the pinned baseline in the repository `.nvmrc`; supported versions are `>=22.12 <27`.
- From the repository root, install the exact workspace dependencies with `npm ci`.
- Copy `apps/web/.env.example` to `apps/web/.env.local` if a non-default API URL is needed. `.env.local` is ignored by Git.
- `VITE_API_BASE_URL` accepts an absolute HTTP(S) URL without credentials/query/fragment, or a same-origin path such as `/api/v1`. If unset, it defaults to `/api/v1`.
- Vite exposes only `VITE_*` variables to client code. These are public build-time values, never credentials; server secrets must not be added here.

## Commands

Run from the repository root:

| Command | Purpose |
|---|---|
| `npm run web:dev` | Start the local Vite development server |
| `npm run web:typecheck` | Type-check the frontend |
| `npm run web:test` | Run frontend tests once |
| `npm run web:build` | Type-check and create the static production build in `apps/web/dist` |

These are also the commands intended for CI. The build contains only static client assets and public configuration.

## Structure

- `src/main.tsx`: app bootstrap and eager public-config validation.
- `src/app`: router, route error fallback, and loading fallback.
- `src/pages`: route-level pages.
- `src/config`: validated public frontend configuration.
- `src/styles.css`: responsive styles, Tailwind entry point, focus states, and reduced-motion handling.
- `src/**/*.test.*`: focused component/configuration tests.
