# Authentication Providers

## Overview

The auth service uses pluggable JWT authentication providers via the Strategy Pattern. Provider implementations live in the `dos-utility` package — see [dos-utility auth docs](../dos-utility/docs/auth/auth.md) for details on how the factory and interface work.

## Configuration

Set the `AUTH_PROVIDER` environment variable to select the provider.

### AWS Cognito

```env
AUTH_PROVIDER=aws
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_COGNITO_USERPOOL_ID=us-east-1_XXXXXXXXX

# Optional: for LocalStack
AWS_ENDPOINT_URL=http://localstack:4566
ENVIRONMENT=test
```

| Variable | Description | Required |
|---|---|---|
| `AWS_REGION` | AWS region of your Cognito user pool; also used to build the Cognito JWKS URL | yes |
| `AWS_COGNITO_USERPOOL_ID` | Your Cognito user pool ID | yes |
| `AWS_ACCESS_KEY_ID` | AWS credentials | yes |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials | yes |
| `AWS_ENDPOINT_URL` | Custom endpoint for local AWS emulation (e.g. LocalStack). `AWSAuthSettings` has no default for it, so it must be set even when targeting real AWS — pass an empty string in that case | yes |
| `ENVIRONMENT` | Set to `test` when using a local AWS emulator (LocalStack, moto). In test mode, JWKS are fetched from `AWS_ENDPOINT_URL` instead of the real AWS Cognito endpoint. Any other value (e.g. `dev`, `production`) uses the real AWS endpoint | no, default `dev` |

### Local (Development Only)

```env
AUTH_PROVIDER=local
```

The local provider has no environment variables of its own

> ⚠️ **WARNING**: The `local` provider bypasses real JWT cryptographic
verification. **Use only for local development.**

- ✅ **Use for**: frontend development, local testing, debugging
- ❌ **Never use in**: staging, production, security testing

#### Local provider behavior

- Accepts tokens of the form `local-token-<role>` where `<role>` is one of the `UserRole` values — currently `user` or `admin`.
- Any other token (including an empty string from a missing or malformed `Authorization` header) is rejected with `InvalidTokenException`, which the service translates to `401`.
- The returned claims depend on the role parsed from the token:
  - `sub` — a stable UUID per role
    (`00000000-0000-0000-0000-000000000001` for `user`,
    `00000000-0000-0000-0000-000000000002` for `admin`)
  - `email` — `<role>@local.example.com`
  - `role` — the parsed `UserRole`
  - plus mock `iss`, `iat`, `exp`, `name`, `cognito:username`,
    `auth_time`, `token_use`, `client_id`

Example requests:
```bash
# As a regular user
curl -H "Authorization: Bearer local-token-user" \
     http://localhost:3000/protected/jwt-check

# As an admin
curl -H "Authorization: Bearer local-token-admin" \
     http://localhost:3000/protected/jwt-check

# Without a header (or any non-dev token) → 401
curl http://localhost:3000/protected/jwt-check
```
