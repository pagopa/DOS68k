# API Gateway

The API Gateway is the single entry point for every request directed at a DOS68K backend service. Frontends, third-party clients and internal tools never talk to a backend directly: they hit the gateway, which authenticates the caller, attaches a trusted identity, and proxies the request to the correct upstream.

DOS68K ships with a [Traefik](https://traefik.io/) configuration as the reference implementation, but the platform does not depend on Traefik itself. Any API gateway that supports a **forward-auth** primitive (NGINX with `auth_request`, Envoy with `ext_authz`, HAProxy, Kong, AWS ALB + Lambda authorizer, etc.) can replace it with no changes to the backend services. The contract described below is the load-bearing part — the gateway product is interchangeable.

## Request flow

```
                +---------------------------+
                |        Frontend           |
                +-------------+-------------+
                              |
                  Authorization: Bearer <token>
                              v
                +---------------------------+
                |        API Gateway        |
                +-------------+-------------+
                              |
              (1) forward-auth: GET /protected/jwt-check
                              v
                +---------------------------+
                |         Auth service      |
                +-------------+-------------+
                              |
              2xx + X-User-Id / X-User-Role  (or 401/403)
                              |
                              v
                +---------------------------+
                |        API Gateway        |
                |   - strip Authorization   |
                |   - inject X-User-Id      |
                |   - inject X-User-Role    |
                +-------------+-------------+
                              |
                              v
                +---------------------------+
                |    Upstream backend       |
                |  (chatbot-api, index, …)  |
                +---------------------------+
```

### Step-by-step

1. **Client → Gateway.** The client sends the request to the gateway with an `Authorization: Bearer <token>` header. The token is opaque to the gateway: it never validates or decodes it.
2. **Gateway → Auth (forward-auth).** Before routing the request, the gateway issues a subrequest to the auth service (`GET /protected/jwt-check`), forwarding the original headers. This happens on every protected request — there is no token caching at the gateway layer.
3. **Auth decides.** The auth service validates the token and answers:
   - **2xx** with `X-User-Id` and `X-User-Role` response headers → the request is allowed.
   - **Non-2xx** (401, 403, …) → the gateway rejects the original request with the same status and the upstream is never called.
4. **Gateway rewrites headers.** On a 2xx auth response, the gateway:
   - **strips** the inbound `Authorization` header (the token never reaches backends),
   - **injects** `X-User-Id` and `X-User-Role` taken from the auth response, overriding any value the client may have supplied.  
   This override is critical: backends trust these headers
   unconditionally, so the gateway must be the only source of truth for them.
5. **Gateway → Upstream.** The rewritten request is proxied to the
   upstream service selected by the routing rules (host, path prefix, etc.).
6. **Backend consumes identity.** Upstream services read identity from `X-User-Id` / `X-User-Role` via the helpers in [`dos_utility.auth`](../dos-utility) (`get_user`, `get_admin_user`).  
They do not parse JWTs themselves.

## Responsibilities of the gateway

The gateway is intentionally thin. Its only required responsibilities are:

- **Routing** — map host/path to the right upstream service.
- **Forward-auth** — call the auth service and gate the request on its response.
- **Header hygiene** — strip `Authorization`, inject `X-User-Id` / `X-User-Role` from the auth response.
- **CORS** — apply CORS policy at a single, central place.
- **Rate limiting** — protect upstreams from abusive clients.
- **TLS termination** (in production deployments).

Everything else — business logic, persistence, RAG orchestration — lives in the backend services.

## Swapping the gateway

To run DOS68K behind a different gateway, the replacement must support:

1. A **forward-auth / external authorization** hook that gates every protected route on a 2xx response from the auth service.
2. The ability to **copy response headers from the auth subrequest onto the upstream request** (`X-User-Id`, `X-User-Role`).
3. The ability to **remove the inbound `Authorization` header** before proxying.

If those three primitives are available, the rest is configuration. The Traefik files in this directory can be used as a reference for the expected behaviour.
