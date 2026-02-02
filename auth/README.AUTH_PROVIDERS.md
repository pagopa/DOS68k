# Adaptive Authentication Layer

## Overview

Questo progetto implementa un **adaptive authentication layer** che consente di utilizzare diversi provider di autenticazione JWT in modo trasparente. L'implementazione utilizza il **Strategy Pattern** con una classe astratta e implementazioni concrete per ogni provider.

## Architettura

### Componenti Principali

```
src/service/
├── auth_provider_base.py      # Classe astratta BaseAuthProvider
├── cognito_auth_provider.py   # Implementazione per AWS Cognito
├── keycloak_auth_provider.py  # Implementazione per Keycloak
├── local_auth_provider.py     # Implementazione local/mock (no verification)
└── __init__.py                # Factory function get_provider()
```

### Diagramma di Classe

```
┌─────────────────────────┐
│   BaseAuthProvider      │ (Abstract)
├─────────────────────────┤
│ + get_jwks()            │ (Abstract)
│ + verify_jwt(token)     │ (Abstract)
└──────────┬──────────────┘
           │
           │ extends
           │
    ┌──────┴──────┬────────────────┐
    │             │                │
┌───▼──────────────────┐  ┌───▼──────────────────┐  ┌───▼──────────────────┐
│ CognitoAuthProvider  │  │ KeycloakAuthProvider │  │ LocalAuthProvider    │
├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤
│ + get_jwks()         │  │ + get_jwks()         │  │ + get_jwks()         │
│ + verify_jwt(token)  │  │ + verify_jwt(token)  │  │ + verify_jwt(token)  │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

## Configurazione

### Variabili d'Ambiente

La selezione del provider avviene tramite la variabile `AUTH_PROVIDER`:

```env
# Scegli il provider: cognito, keycloak, local
AUTH_PROVIDER=cognito
ENVIRONMENT=development
```

#### Configurazione AWS Cognito

```env
AUTH_PROVIDER=cognito
AWS_REGION=us-east-1
AWS_COGNITO_REGION=us-east-1
AUTH_COGNITO_USERPOOL_ID=us-east-1_XXXXXXXXX

# Per sviluppo locale con LocalStack
AWS_ENDPOINT_URL=http://localstack:4566
```

#### Configurazione Keycloak

```env
AUTH_PROVIDER=keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=your-realm
```

#### Configurazione Local (Development Only)

```env
# ⚠️ SOLO PER SVILUPPO - Disabilita la verifica JWT
AUTH_PROVIDER=local
```

**⚠️ ATTENZIONE**: Il provider `local` **bypassa completamente la verifica JWT** e ritorna sempre un successo con claims mock. 

**Usare SOLO in ambiente di sviluppo locale!**

- ✅ Utile per: sviluppo frontend, test locali, debugging
- ❌ NON usare in: staging, produzione, test di sicurezza

**Comportamento speciale in modalità local:**
- L'header `Authorization` diventa **opzionale** - puoi chiamare l'endpoint anche senza token
- Qualsiasi token (anche malformato) viene accettato
- Ritorna sempre gli stessi claims mock

Il provider local ritorna sempre questi claims:
```json
{
  "sub": "local-user-123",
  "email": "local@example.com",
  "name": "Local Development User",
  "exp": 9999999999
}
```

**Esempio di utilizzo:**
```bash
# Senza header (funziona solo con AUTH_PROVIDER=local)
curl http://localhost:8000/protected/jwt-check

# Con header (funziona sempre)
curl -H "Authorization: Bearer any-token" \
     http://localhost:8000/protected/jwt-check
```

## Utilizzo

### 1. Utilizzo nel Router

```python
from fastapi import APIRouter, Header, HTTPException, status
from ..service.jwt_chesck_service import verify_jwt_token

router = APIRouter(prefix="/protected", tags=["JWT Protected"])

@router.get("/jwt-check")
def jwt_check(Authorization: str = Header(...)):
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing Bearer token")
    
    token = Authorization.split(" ", 1)[1]
    payload = verify_jwt_token(token)
    
    return {"status": "ok", "payload": payload}
```

### 2. Utilizzo Diretto del Provider

```python
from src.service.auth_provider_factory import get_auth_provider

# Ottieni il provider configurato (singleton)
provider = get_auth_provider()

# Verifica un token JWT
claims = provider.verify_jwt(token)

# Ottieni le chiavi pubbliche
jwks = provider.get_jwks()
```

## Aggiungere un Nuovo Provider

Per aggiungere un nuovo provider di autenticazione (es. Auth0, Okta):

### 1. Crea una Nuova Implementazione

```python
# src/service/auth0_auth_provider.py
from .auth_provider_base import BaseAuthProvider
from typing import Dict, Any

class Auth0AuthProvider(BaseAuthProvider):
    def __init__(self):
        self.domain = SETTINGS.auth0_domain
        self.audience = SETTINGS.auth0_audience
    
    def get_jwks(self) -> Dict[str, Any]:
        # Implementa la logica per Auth0
        keys_url = f"https://{self.domain}/.well-known/jwks.json"
        response = requests.get(keys_url)
        return response.json()
    
    def verify_jwt(self, token: str) -> Dict[str, Any]:
        # Implementa la logica di verifica per Auth0
        ...
```

### 2. Registra il Provider nella Factory

```python
# src/service/auth_provider_factory.py
from .auth0_auth_provider import Auth0AuthProvider

class AuthProviderFactory:
    PROVIDERS = {
        "cognito": CognitoAuthProvider,
        "keycloak": KeycloakAuthProvider,
        "auth0": Auth0AuthProvider,  # ← Aggiungi qui
    }
```

### 3. Aggiungi le Variabili d'Ambiente

```python
# src/modules/settings.py
class Settings(BaseSettings):
    # ...esistenti...
    
    # Auth0 Settings
    auth0_domain: Annotated[Optional[str], Field(default=None)]
    auth0_audience: Annotated[Optional[str], Field(default=None)]
```

### 4. Usa il Nuovo Provider

```env
AUTH_PROVIDER=auth0
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=your-api-identifier
```

## Vantaggi dell'Architettura

### ✅ Separazione delle Responsabilità
Ogni provider è isolato nella propria classe con la propria logica.

### ✅ Open/Closed Principle
Il sistema è aperto all'estensione (nuovi provider) ma chiuso alla modifica (codice esistente non cambia).

### ✅ Dependency Inversion
Il codice dipende dall'astrazione (`BaseAuthProvider`), non dalle implementazioni concrete.

### ✅ Facilità di Test
Puoi facilmente creare mock del provider per i test:

```python
class MockAuthProvider(BaseAuthProvider):
    def get_jwks(self):
        return {"keys": []}
    
    def verify_jwt(self, token: str):
        return {"sub": "test-user", "exp": 9999999999}
```

### ✅ Configurazione Trasparente
Il cambio di provider avviene solo modificando una variabile d'ambiente, senza toccare il codice.

## Testing

### Test con Provider Mock

```python
# test/test_jwt_service.py
from src.service.auth_provider_factory import AuthProviderFactory
from src.service.auth_provider_base import BaseAuthProvider

class TestAuthProvider(BaseAuthProvider):
    def get_jwks(self):
        return {"keys": [{"kid": "test", "kty": "RSA"}]}
    
    def verify_jwt(self, token: str):
        return {"sub": "test-user"}

# Registra il provider di test
AuthProviderFactory.PROVIDERS["test"] = TestAuthProvider

# Usa il provider di test
provider = AuthProviderFactory.create_provider("test")
```

## API Endpoints

### GET /protected/jwt-check

Verifica un token JWT usando il provider configurato.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "status": "ok",
  "payload": {
    "sub": "user-id",
    "exp": 1234567890,
    "iat": 1234567800,
    ...
  }
}
```

**Errors:**
- `401 Unauthorized`: Token non valido, scaduto o mancante

## Migrazione dal Codice Precedente

Il codice esistente continua a funzionare grazie alla funzione `verify_jwt_token` che è un alias di `verify_jwt`. Tuttavia, è consigliato aggiornare i riferimenti:

**Prima:**
```python
from src.service.jwt_chesck_service import verify_jwt
```

**Dopo (opzionale, stessa cosa):**
```python
from src.service.jwt_chesck_service import verify_jwt_token
```

**Oppure usa direttamente il provider:**
```python
from src.service.auth_provider_factory import get_auth_provider

provider = get_auth_provider()
claims = provider.verify_jwt(token)
```

## Troubleshooting

### Errore: "Unsupported auth provider"

Verifica che la variabile `AUTH_PROVIDER` sia impostata correttamente e che il valore corrisponda a un provider registrato nella factory.

### Errore: "Keycloak configuration incomplete"

Se usi Keycloak, assicurati di aver impostato `KEYCLOAK_URL` e `KEYCLOAK_REALM`.

### Errore: "Auth error" durante get_jwks

Verifica che:
- L'URL del provider sia raggiungibile
- Le credenziali (se necessarie) siano corrette
- La configurazione del provider sia completa

## Riferimenti

- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Factory Pattern](https://refactoring.guru/design-patterns/factory-method)
- [AWS Cognito JWKS](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html)
- [Keycloak OIDC](https://www.keycloak.org/docs/latest/securing_apps/#_oidc)
