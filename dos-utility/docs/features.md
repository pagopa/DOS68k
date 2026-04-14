# Features

Here a list of functionalities this package provide:

- [Auth interface](#2-auth-interface)
- [Queue interface](#3-queue-interface)
- [Storage interface](#4-storage-interface)
- [VectorDB interface](#5-vector-db-interface)
- [NoSQL DB interface](#6-nosql-db-interface)
- [Utilities](#7-utilities)

## 1. SQL DB connection

> !!!! THIS SQL MODULE IS NOT USED IN THE PROJECT !!!!

This module provides an async SQLAlchemy session factory for PostgreSQL, using the `asyncpg` driver.

### 1.1 Env setup

Create a `.env` file with the following variables (all have defaults for local development):

```bash
export DB_USERNAME=<username>      # Default: postgres
export DB_PASSWORD=<password>      # Default: password
export DB_HOST=<host>              # Default: localhost
export DB_PORT=<port>              # Default: 5432
export DB_NAME=<database-name>     # Default: db
```

### 1.2 How to use it

```python
from dos_utility.database.sql import get_async_session
```

Use it as a FastAPI dependency:

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dos_utility.database.sql import get_async_session

@app.get("/items")
async def get_items(session: Annotated[AsyncSession, Depends(get_async_session)]):
    result = await session.execute(...)
```

For more details, check [sql.md](./database/sql/sql.md).

## 2. Auth interface

This is an adaptive layer, implemented as an interface, to manage authentication and JWT verification. Currently supported providers:

- AWS Cognito
- Local (for development/testing)

### 2.1 Env setup

First of all, since this is an intermediate layer, which can have multiple implementations, you need to configure your environment variables to select and configure the right provider. In your project create a `.env` file like this:

```bash
export AUTH_PROVIDER=<provider>
```

As for now, valid values are `aws`/`local`.<br>
Once you decided the provider, you have to set other env variables which are specific to that provider. Below you can find details about each provider.

#### 2.1.1 AWS Cognito env

Add the following env variables to the `.env` file you created [here](#21-env-setup).

```bash
export AWS_REGION=<region>
export AWS_ENDPOINT_URL=<endpoint> # With format http(s)://host (es: http://cognito-local.us-east-1.amazonaws.com)
export AWS_ACCESS_KEY_ID=<access-key-id>
export AWS_SECRET_ACCESS_KEY=<secret-access-key>
export AWS_COGNITO_USERPOOL_ID=<user-pool-id>
export ENVIRONMENT=<environment> # Optional, default: dev. Use 'test' for local development with mock Cognito
```

#### 2.1.2 Local env

The local provider doesn't require any additional environment variables besides `AUTH_PROVIDER=local`. It's designed for development and testing purposes and will bypass JWT verification, always returning mock claims.

**WARNING**: Never use the local provider in production environments as it completely disables authentication.

### 2.2 How to use it

You always want to use the interface in your code, not the actual implementation of a specific provider, so that you can benefit from this abstraction layer, without the need to change the code as the provider changes.<br>
Here a code snippet for the import.

```python
from dos_utility.auth import AuthInterface, get_auth
from dos_utility.auth import EmptyTokenException, TokenExpiredException, InvalidTokenException, InvalidTokenKeyException
```

Example usage:

```python
# Get the auth provider instance
auth_provider: AuthInterface = get_auth()

# Retrieve JWKS (JSON Web Key Set)
jwks = auth_provider.get_jwks()

# Verify a JWT token
token = "eyJhbGc..."  # Your JWT token
try:
    claims = auth_provider.verify_jwt(token)
    user_id = claims.get("sub")
    email = claims.get("email")
    # Process the authenticated user
except EmptyTokenException:
    # Handle empty token
    ...
except TokenExpiredException:
    # Handle expired token
    ...
except (InvalidTokenException, InvalidTokenKeyException) as e:
    # Handle invalid token
    ...
```

The interface provides two main methods:

- `get_jwks()`: Retrieves the JSON Web Key Set from the authentication provider
- `verify_jwt(token: str)`: Verifies a JWT token and returns its claims

For the full interface spec, check [auth_interface.md](./auth/auth_interface.md).

### 2.3 Implement new provider

If you want to provide a new implementation for a different provider you are welcome, just make sure to respect some standards:

- create a class which implements the `AuthInterface` (see `src/dos_utility/auth/interface.py`). Write your own code in a dedicated folder under `src/dos_utility/auth` module.
- update the `get_auth` with your new implementation, under `src/dos_utility/auth/__init__.py`.
- add the new provider to the `AuthProvider` enum in `src/dos_utility/auth/env.py`.
- write unit tests for your new implementation and for the updated `get_auth`.
- update this doc so that the documentation is up to date.

### 2.4 Update the interface

It could be possible that the actual interface doesn't cover some needed behaviors or some vendors functionalities. If you want to update it you can do it, but be sure to align all pre-existing provider implementations and update unit-tests. Other than that, check each micro-service which use that interface and make sure it doesn't break with the new structure.

## 3. Queue interface

This is an adaptive layer, implemented as an interface, to manage a connection with a queue. Currently supported queues:

- SQS
- Redis

### 3.1 Env setup

First of all, since this is an intermediate layer, which can have multiple implementations, you need to configure your environment variables to select and configure the right provider. In your project create a `.env` file like this:

```bash
export QUEUE_PROVIDER=<provider>
```

As for now, valid values are `sqs`/`redis`.<br>
Once you decided the provider, you have to set other env variables which are specific to that provider. Below you can find details about each provider.

#### 3.1.1 SQS env

Add the following env variables to the `.env` file you created [here](#31-env-setup).

```bash
export SQS_ENDPOINT_URL=<endpoint> # With format http(s)://host (es: http://localstack)
export SQS_PORT=<port>             # Default: 4566
export SQS_REGION=<region>         # Default: us-east-1
export AWS_ACCESS_KEY_ID=<access-key-id>
export AWS_SECRET_ACCESS_KEY=<secret-access-key>
export SQS_QUEUE_NAME=<queue-name>
export SQS_QUEUE_URL=<queue-url>
```

#### 3.1.2 Redis env

Add the following env variables to the `.env` file you created [here](#31-env-setup).

```bash
export REDIS_HOST=<host> # with format <host>, without protocol (es: queue - as per the name in the docker compose)
export REDIS_PORT=<port>
export REDIS_STREAM=<stream-name>  # Default: my-stream
export REDIS_GROUP=<group-name>    # Default: my-group
```

### 3.2 How to use it

You always want to use the interface in your code, not the actual implementation of a specific provider, so that you can benefit from this abstraction layer, without the need to change the code as the provider changes.<br>
Here a code snippet for the import.

```python
# You choose whether to use get_queue_client or get_queue_client_ctx, based on your needs
from dos_utility.queue import QueueInterface, get_queue_client, get_queue_client_ctx
```

In order to have better understanding of each element, checkout [queue.md](./queue/queue.md) to see examples and [queue_interface.md](./queue/queue_interface.md) to find out what methods are available for the interface.

### 3.3 Implement new provider

If you want to provide a new implementation for a different provider you are welcome, just make sure to respect some standards:

- create a class which implements the `QueueInterface` ([here](./queue/queue_interface.md) the specs), under `src/dos_utility/queue/interface.py`. Write your own code in a dedicated folder under `src/dos_utility/queue` module.
- update the `get_queue_client_ctx` with your new implementation, under `src/dos_utility/queue/__init__.py`.
- add the new provider to the `QueueProvider` enum in `src/dos_utility/queue/env.py`.
- write unit tests for your new implementation and for the updated `get_queue_client_ctx`.
- update this doc so that the documentation is up to date.

### 3.4 Update the interface

It could be possible that the actual interface doesn't cover some needed behaviors or some vendors functionalities. If you want to update it you can do it, but be sure to align all pre-existing provider implementations and update unit-tests. Other than that, check each micro-service which use that interface and make sure it doesn't break with the new structure.

## 4. Storage interface

This is an adaptive layer, implemented as an interface, to manage a connection with a storage service. Currently supported storage:

- AWS S3
- MinIO

### 4.1 Env setup

First of all, since this is an intermediate layer, which can have multiple implementations, you need to configure your environment variables to select and configure the right provider. In your project create a `.env` file like this:

```bash
export STORAGE_PROVIDER=<provider>
```

As for now, valid values are `aws_s3`/`minio`.<br>
Once you decided the provider, you have to set other env variables which are specific to that provider. Below you can find details about each provider.

#### 4.1.1 AWS S3 env

Add the following env variables to the `.env` file you created [here](#41-env-setup).

```bash
export S3_ENDPOINT=<endpoint> # This is optional. If you are working with real AWS S3 then you can omit it, while if you are working with S3 local implementations (say LocalStack) then you have to specify the endpoint
export S3_REGION=<region>
export AWS_ACCESS_KEY_ID=<access-key-id>
export AWS_SECRET_ACCESS_KEY=<secret-access-key>
```

#### 4.1.2 MinIO env

Add the following env variables to the `.env` file you created [here](#41-env-setup).

```bash
export MINIO_ENDPOINT=<endpoint> # with format <host>, without protocol (es. storage - as per docker compose service name)
export MINIO_PORT=<port>
export MINIO_ACCESS_KEY=<access-key>
export MINIO_SECRET_KEY=<secret-key>
export MINIO_REGION=<region>
export MINIO_SECURE=<bool> # true/false. true if you want to use HTTPS protocol, false if you use HTTP
```

### 4.2 How to use it

You always want to use the interface in your code, not the actual implementation of a specific provider, so that you can benefit from this abstraction layer, without the need to change the code as the provider changes.<br>
Here a code snippet for the import.

```python
from dos_utility.storage import StorageInterface, ObjectInfo, get_storage
```

In order to have better understanding of each element, checkout [storage.md](./storage/storage.md) to see examples and [storage_interface.md](./storage/storage_interface.md) to find out what methods are available for the interface.

### 4.3 Implement new provider

If you want to provide a new implementation for a different provider you are welcome, just make sure to respect some standards:

- create a class which implements the `StorageInterface` ([here](./storage/storage_interface.md) the specs), under `src/dos_utility/storage/interface.py`. Write your own code in a dedicated folder under `src/dos_utility/storage` module.
- update the `get_storage` with your new implementation, under `src/dos_utility/storage/__init__.py`.
- add the new provider to the `StorageProvider` enum in `src/dos_utility/storage/env.py`.
- write unit tests for your new implementation and for the updated `get_storage`.
- update this doc so that the documentation is up to date.

### 4.4 Update the interface

It could be possible that the actual interface doesn't cover some needed behaviors or some vendors functionalities. If you want to update it you can do it, but be sure to align all pre-existing provider implementations and update unit-tests. Other than that, check each micro-service which use that interface and make sure it doesn't break with the new structure.

## 5. Vector DB interface

This is an adaptive layer, implemented as an interface, to manage a connection and its methods with a vector database. Currently supported dbs:

- Qdrant
- Redis

The interface also provides LlamaIndex integration through the `aquery` method (via `BasePydanticVectorStore`).

### 5.1 Env setup

First of all, since this is an intermediate layer, which can have multiple implementations, you need to configure your environment variables to select and configure the right provider. In your project create a `.env` file like this:

```bash
export VECTOR_DB_PROVIDER=<provider>
```

As for now, valid values are `qdrant`/`redis`.<br>
Once you decided the provider, you have to set other env variables which are specific to that provider. Below you can find details about each provider.

#### 5.1.1 Qdrant env

Add the following env variables to the `.env` file you created [here](#51-env-setup).

```bash
export QDRANT_HOST=<host> # With format <host> (es: localhost)
export QDRANT_PORT=<port> # Default: 6333
```

#### 5.1.2 Redis env

Add the following env variables to the `.env` file you created [here](#51-env-setup).

```bash
export REDIS_HOST=<host> # with format <host>, without protocol (es: queue - as per the name in the docker compose)
export REDIS_PORT=<port> # Default: 6379
```

### 5.2 How to use it

You always want to use the interface in your code, not the actual implementation of a specific provider, so that you can benefit from this abstraction layer, without the need to change the code as the provider changes.<br>
Here a code snippet for the import.

```python
# You choose whether to use get_vector_db, get_vector_db_ctx, or get_vector_db_instance based on your needs
from dos_utility.vector_db import VectorDBInterface, ObjectData, SearchResult, get_vector_db_ctx, get_vector_db, get_vector_db_instance
from dos_utility.vector_db import IndexCreationException, IndexDeletionException, PutObjectsException, DeleteObjectsException
```

There are three factory functions:

- `get_vector_db_ctx(index_name=None)` - async context manager for standalone scripts or workers
- `get_vector_db(index_name=None)` - FastAPI dependency (same behavior, works with `Depends()`)
- `get_vector_db_instance(index_name=None)` - returns an instance directly, without a context manager. Intended for LlamaIndex integration (`VectorStoreIndex.from_vector_store`)

In order to have better understanding of each element, checkout [vector_db.md](./vector_db/vector_db.md) to see examples and [vector_db_interface.md](./vector_db/vector_db_interface.md) to find out what methods are available for the interface.

### 5.3 Implement new provider

If you want to provide a new implementation for a different provider you are welcome, just make sure to respect some standards:

- create a class which implements the `VectorDBInterface` ([here](./vector_db/vector_db_interface.md) the specs), under `src/dos_utility/vector_db/interface.py`. Write your own code in a dedicated folder under `src/dos_utility/vector_db` module.
- update the `get_vector_db_ctx` with your new implementation, under `src/dos_utility/vector_db/__init__.py`.
- add the new provider to the `VectorDBProvider` enum in `src/dos_utility/vector_db/env.py`.
- write unit tests for your new implementation and for the updated `get_vector_db_ctx`.
- update this doc so that the documentation is up to date.

### 5.4 Update the interface

It could be possible that the actual interface doesn't cover some needed behaviors or some vendors functionalities. If you want to update it you can do it, but be sure to align all pre-existing provider implementations and update unit-tests. Other than that, check each micro-service which use that interface and make sure it doesn't break with the new structure.

## 6. NoSQL DB interface

This is an adaptive layer, implemented as an interface, to manage a connection and CRUD operations with a NoSQL database. Currently supported databases:

- AWS DynamoDB

### 6.1 Env setup

First of all, since this is an intermediate layer, which can have multiple implementations, you need to configure your environment variables to select and configure the right provider. In your project create a `.env` file like this:

```bash
export NOSQL_PROVIDER=<provider>
```

As for now, valid values are `dynamodb`.<br>
Once you decided the provider, you have to set other env variables which are specific to that provider. Below you can find details about each provider.

#### 6.1.1 DynamoDB env

Add the following env variables to the `.env` file you created [here](#61-env-setup).

```bash
export AWS_ACCESS_KEY_ID=<access-key-id>
export AWS_SECRET_ACCESS_KEY=<secret-access-key>
export DYNAMODB_REGION=<region> # Optional, defaults to us-east-1
export DYNAMODB_ENDPOINT_URL=<endpoint> # Optional. With format http(s)://host (e.g. http://localhost). Omit for real AWS DynamoDB
export DYNAMODB_PORT=<port> # Optional. Port for the endpoint URL
export DYNAMODB_TABLE_PREFIX=<prefix> # Optional. Prefix prepended to all table names
```

### 6.2 How to use it

You always want to use the interface in your code, not the actual implementation of a specific provider, so that you can benefit from this abstraction layer, without the need to change the code as the provider changes.<br>
Here a code snippet for the import.

```python
# You choose whether to use get_nosql_client or get_nosql_client_ctx, based on your needs
from dos_utility.database.nosql import NoSQLInterface, KeyCondition, ConditionOperator, QueryResult, ScanResult, get_nosql_client, get_nosql_client_ctx
```

In order to have better understanding of each element, checkout [nosql.md](./database/nosql/nosql.md) to see examples and [nosql_interface.md](./database/nosql/nosql_interface.md) to find out what methods are available for the interface.

### 6.3 Implement new provider

If you want to provide a new implementation for a different provider you are welcome, just make sure to respect some standards:

- create a class which implements the `NoSQLInterface` ([here](./database/nosql/nosql_interface.md) the specs), under `src/dos_utility/database/nosql/interface.py`. Write your own code in a dedicated folder under `src/dos_utility/database/nosql` module.
- update the `get_nosql_client_ctx` with your new implementation, under `src/dos_utility/database/nosql/__init__.py`.
- add the new provider to the `NoSQLProvider` enum in `src/dos_utility/database/nosql/env.py`.
- write unit tests for your new implementation and for the updated `get_nosql_client_ctx`.
- update this doc so that the documentation is up to date.

### 6.4 Update the interface

It could be possible that the actual interface doesn't cover some needed behaviors or some vendors functionalities. If you want to update it you can do it, but be sure to align all pre-existing provider implementations and update unit-tests. Other than that, check each micro-service which use that interface and make sure it doesn't break with the new structure.

## 7. Utilities

Shared utility modules used across the package.

### 7.1 Logger

A pre-configured logger factory that outputs to `stdout` with a standard format.

```python
from dos_utility.utils.logger import get_logger

logger = get_logger(name=__name__)
logger.info("Something happened")
```

### 7.2 AWS credentials

Shared AWS credentials settings, used by modules that need AWS access (SQS, DynamoDB, S3).

```python
from dos_utility.utils.aws import get_aws_credentials_settings, AWSCredentialsSettings
```

Required env variables:

```bash
export AWS_ACCESS_KEY_ID=<access-key-id>
export AWS_SECRET_ACCESS_KEY=<secret-access-key>
```

### 7.3 Redis connection pool

Shared async Redis connection pool, used by modules that need Redis access (Queue, VectorDB).

```python
from dos_utility.utils.redis import get_redis_connection_pool
```

Required env variables:

```bash
export REDIS_HOST=<host>  # Default: localhost
export REDIS_PORT=<port>  # Default: 6379
```
