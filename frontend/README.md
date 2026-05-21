# Frontend

This frontend is an **optional** module of DOS68K. The platform runs without it — it ships as a reference UI to exercise the backend locally and as a starting point for a real client. It is not production-ready.

## Tech stack

- React 19 + TypeScript
- Vite 7 (build) / Vitest + MSW (tests)
- React Router 7
- TanStack Query 5
- Tailwind CSS v4 + Radix UI primitives
- Served in production by nginx (see `Dockerfile`, `nginx.conf`)

## Roles

The UI has two hardcoded roles. The role is selected at login and gates which pages are reachable:

| Role | Can access | What they see |
|------|------------|---------------|
| `user`  | `/chat` | Sessions sidebar, message composer, message list with sources |
| `admin` | `/chat` + `/admin` | Everything above plus index management, document upload/delete, and a backend health strip (queue / storage / vector DB) |

## Authentication — dev/demo only

> The login screen ("Continue as User" / "Continue as Admin") is **not real authentication**. It stores a placeholder bearer token (`local-token-<role>`) in `localStorage` and is intended exclusively for local testing against the `auth` service running in `AUTH_PROVIDER=local` mode. See more [here](../auth/README.AUTH_PROVIDERS.md#local-provider-behavior).
>
> Against a real IdP (Cognito, Keycloak), this flow will not work — the gateway's forward-auth check will reject the placeholder token. Replacing `src/lib/auth/local-auth.ts` with a provider that obtains a real JWT is required before any non-local use.

## Configuration

`VITE_API_BASE_URL` is the only configuration knob. It must point at the **API gateway** (not at individual services), since the gateway is what authenticates and routes to `chatbot-api` and `chatbot-index/api`.

- Build-time placeholder: the Docker image is built with `VITE_API_BASE_URL=__API_BASE_URL__`. At container start, `docker-entrypoint.sh` substitutes the placeholder in the built JS with the runtime value of `VITE_API_BASE_URL`. This means one image works for any deployment target.
- Default in `compose.yaml`: `http://localhost:8080` (the API gateway).

## Run via Docker Compose

From the repo root:

```bash
docker compose up -d --build frontend
```

The UI is then served at `http://localhost:80`. Note that port 80 may require root on Linux and conflicts with any other process bound to it — adjust the port mapping in `compose.yaml` if needed.

## Local development

Prerequisites: `pnpm` (or `npm`) and Node.js 22+.

```bash
pnpm install
pnpm dev          # Vite dev server with HMR
pnpm test         # Vitest, one-shot
pnpm test:watch   # Vitest, watch mode
pnpm lint         # ESLint
pnpm build        # Type-check + production build to dist/
```

During `pnpm dev`, set `VITE_API_BASE_URL` in a `.env` file at `frontend/` to point at your gateway, e.g. `VITE_API_BASE_URL=http://localhost:8080`.
