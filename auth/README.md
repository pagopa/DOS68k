# Authentication Service

The identity verifier for DOS68K. The API gateway calls it on every protected
request to decide who the caller is and whether to let them through.

For the big picture, see [Overview](../docs/overview.md) and especially
[the authentication model](../docs/overview.md#authentication-model).

## Role in the platform

This service is the gateway's **forward-auth** target. On each protected
request, the gateway hands it the caller's login token; the service validates
the token and answers with the caller's identity (**id** and **role**), which
the gateway then attaches to the request before forwarding it to the backends.
Backends never see the raw token — only the identity this service vouches for.

> This is **not** an identity provider. It only *verifies* tokens; it does not
> create accounts or issue logins. Sign-in and user management happen in the
> external provider you connect.

## Providers

Selected with `AUTH_PROVIDER`:

- **Local (default)** — a mock for development and demos. It accepts placeholder
  tokens and performs **no real authentication**. Never use it in production.
- **AWS Cognito** — validates real Cognito-issued tokens. Your users sign in
  through Cognito, and you provision admin vs. user identities there.

Provider connection settings are documented in
[the dos-utility auth reference](../dos-utility/docs/features.md#2-auth-interface);
provider-specific behaviour and setup are in
[README.AUTH_PROVIDERS.md](./README.AUTH_PROVIDERS.md).
</content>
