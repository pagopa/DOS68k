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
| `AWS_REGION` | AWS region of your Cognito user pool | yes |
| `AWS_COGNITO_REGION` | Region used to build the Cognito JWKS URL | yes |
| `AUTH_COGNITO_USERPOOL_ID` | Your Cognito user pool ID | yes |
| `AWS_ACCESS_KEY_ID` | AWS credentials | yes |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials | yes |
| `AWS_ENDPOINT_URL` | Custom endpoint for local AWS emulation (e.g. LocalStack). Omit for real AWS | no |
| `ENVIRONMENT` | Set to `test` when using a local AWS emulator (LocalStack, moto). In test mode, JWKS are fetched from `AWS_ENDPOINT_URL` instead of the real AWS Cognito endpoint. Any other value (e.g. `dev`, `production`) uses the real AWS endpoint | no, default `dev` |

### Local (Development Only)

```env
AUTH_PROVIDER=local
JWT_SECRET_KEY=dev-secret-key-not-for-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

| Variable | Description | Default |
|---|---|---|
| `JWT_SECRET_KEY` | Secret key used to sign local mock tokens | required |
| `JWT_ALGORITHM` | Signing algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry duration in minutes | `30` |

⚠️ **WARNING**: The `local` provider bypasses JWT verification entirely and always returns mock claims. **Use only for local development.**

- ✅ **Use for**: frontend development, local testing, debugging
- ❌ **Never use in**: staging, production, security testing

**Local provider behavior**:
- `Authorization` header is optional — missing or malformed headers fall back to an empty token, which the local provider accepts
- Always returns the same mock claims

Example requests:
```bash
# Without header (local mode only)
curl http://localhost:3000/protected/jwt-check

# With header (all modes)
curl -H "Authorization: Bearer <token>" \
     http://localhost:3000/protected/jwt-check
```

## Adding New Providers

See [dos-utility auth interface docs](../dos-utility/docs/auth/auth_interface.md#implementing-a-new-provider) for implementation guidelines (typed exceptions, `token == ""` guard) and [dos-utility auth docs](../dos-utility/docs/auth/auth.md#adding-a-new-provider) for how to register a new provider in the factory.

## API Endpoints

### GET /protected/jwt-check

Verifies a JWT token.

**Request**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200):
```json
{
  "status": "ok",
  "payload": {
    "sub": "user-id",
    "iss": "https://...",
    "exp": 1234567890,
    "iat": 1234567890,
    "email": "user@example.com"
  }
}
```

**Errors**:
- `401`: Invalid, expired, or missing token
