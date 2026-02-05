# Features

Here a list of functionalities this package provide:

- [SQL DB connection](#1-sql-db-connection)
- [Queue interface](#2-queue-interface)
- [Storage interface](#3-storage-interface)
- [VectorDB interface](#4-vector-db)

## 1. SQL DB connection

## 2. Queue interface

This is an adaptive layer, implemented as an interface, to manage a connection with a queue. Actually supported queues:

- SQS
- Redis

### 2.1 Env setup

First of all, since this is an intermediate layer, which can have multiple implementations, you need to configure your environment variables to select and configure the right provider. In your project create a `.env` file like this:

```bash
export QUEUE_PROVIDER=<provider>
```

As for now, valid values are `sqs`/`redis`.<br>
Once you decided the provider, you have to set other env variables which are specific to that provider. Below you can find details about each provider.

#### 2.1.1 SQS env

Add the following env variables to the `.env` file you created [here](#21-env-setup).

```bash
export SQS_ENDPOINT=<endpoint> # With format http(s)://host (es: http://localstack)
export SQS_PORT=<port>
export SQS_REGION=<region>
export AWS_ACCESS_KEY_ID=<access-key-id>
export AWS_SECRET_ACCESS_KEY=<secret-access-key>
export SQS_QUEUE_NAME=<queue-name>
export SQS_QUEUE_URL=<queue-url>
```

#### 2.1.2 Redis env

Add the following env variables to the `.env` file you created [here](#21-env-setup).

```bash
export REDIS_HOST=<host> # with format <host>, without protocol (es: queue - as per the name in the docker compose)
export REDIS_PORT=<port>
export REDIS_STREAM=<stream-name>
export REDIS_GROUP=<group-name>
```

### 2.2 How to use it

You always want to use the interface in your code, not the actual implementation of a specific provider, so that you can benefit from this abstraction layer, without the need to change the code as the provider changes.<br>
Here a code snipped for the import.

```python
# You choose whether to use get_queue_client or get_queue_client_ctx, based on your needs
from dos_utility.queue import QueueInterface, get_queue_client, get_queue_client_ctx
```

In order to have better understanding of each element, checkout [queue.md](./queue/queue.md) to see examples and [queue_interface.md](./queue/queue_interface.md) to find out what methods are available for the interface.

### 2.3 Implement new provider

If you want to provide a new implementation for a different provider you are welcome, just make sure to respect some standards:

- create a class which implements the `QueueInterface` ([here](./queue/queue_interface.md) the specs), under `src/dos_utility/queue/interface.py`. Write your own code in a dedicated folder under `src/dos_utility/queue` module.
- update the `get_queue_client_ctx` with your new implementation, under `src/dos_utility/queue/__init__.py`.
- write unit tests for your new implementation and for the updated `get_queue_client_ctx`.
- update this doc so that the documentation is up to date.

### 2.4 Update the interface

It could be possible that the actual interface doesn't cover some needed behaviors or some vendors functionalities. If you want to update it you can do it, but be sure to align all pre-existing provider implementations and update unit-tests. Other than that, check each micro-service which use that interface and make sure it doesn't break with the new structure.

## 3. Storage interface

This is an adaptive layer, implemented as an interface, to manage a connection with a storage service. Actually supported storage:

- AWS S3
- MinIO

### 3.1 Env setup

First of all, since this is an intermediate layer, which can have multiple implementations, you need to configure your environment variables to select and configure the right provider. In your project create a `.env` file like this:

```bash
export STORAGE_PROVIDER=<provider>
```

As for now, valid values are `aws_s3`/`minio`.<br>
Once you decided the provider, you have to set other env variables which are specific to that provider. Below you can find details about each provider.

#### 3.1.1 AWS S3 env

Add the following env variables to the `.env` file you created [here](#31-env-setup).

```bash
export S3_ENDPOINT=<endpoint> # This is optional. If you are working with real AWS S3 then you can omit it, while if you are working with S3 local implementations (say LocalStack) then you have to specify the endpoint
export S3_REGION=<region>
export AWS_ACCESS_KEY_ID=<access-key-id>
export AWS_SECRET_ACCESS_KEY=<secret-access-key>
```

#### 3.1.2 MinIO env

Add the following env variables to the `.env` file you created [here](#31-env-setup).

```bash
export MINIO_ENDPOINT=<endpoint> # with format <host>, whitout protocol (es. storage - as per docker compose service name)
export MINIO_PORT=<port>
export MINIO_ACCESS_KEY=<access-key>
export MINIO_SECRET_KEY=<secret-key>
export MINIO_REGION=<region>
export MINIO_SECURE=<bool> # true/false. true if you want to use HTTPS protocol, false if you use HTTP
```

### 3.2 How to use it

You always want to use the interface in your code, not the actual implementation of a specific provider, so that you can benefit from this abstraction layer, without the need to change the code as the provider changes.<br>
Here a code snipped for the import.

```python
from dos_utility.storage import StorageInterface, get_storage
```

In order to have better understanding of each element, checkout [storage.md](./storage/storage.md) to see examples and [storage_interface.md](./storage/storage_interface.md) to find out what methods are available for the interface.

### 3.3 Implement new provider

If you want to provide a new implementation for a different provider you are welcome, just make sure to respect some standards:

- create a class which implements the `StorageInterface` ([here](./storage/storage_interface.md) the specs), under `src/dos_utility/storage/interface.py`. Write your own code in a dedicated folder under `src/dos_utility/storage` module.
- update the `get_storage` with your new implementation, under `src/dos_utility/storage/__init__.py`.
- write unit tests for your new implementation and for the updated `get_storage`.
- update this doc so that the documentation is up to date.

### 3.4 Update the interface

It could be possible that the actual interface doesn't cover some needed behaviors or some vendors functionalities. If you want to update it you can do it, but be sure to align all pre-existing provider implementations and update unit-tests. Other than that, check each micro-service which use that interface and make sure it doesn't break with the new structure.

## 4. Vector DB

This is an adaptive layer, implemented as an interface, to manage a connection and its methods with a vector database. Actually supported dbs:

- Qdrant
- Redis

### 4.1 Env setup

First of all, since this is an intermediate layer, which can have multiple implementations, you need to configure your environment variables to select and configure the right provider. In your project create a `.env` file like this:

```bash
export VECTOR_DB_PROVIDER=<provider>
```

As for now, valid values are `qdrant`/`redis`.<br>
Once you decided the provider, you have to set other env variables which are specific to that provider. Below you can find details about each provider.

#### 4.1.1 Qdrant env

Add the following env variables to the `.env` file you created [here](#41-env-setup).

```bash
export QDRANT_HOST=<host> # With format <host> (es: localhost)
export QDRANT_PORT=<port>
```

#### 4.1.2 Redis env

Add the following env variables to the `.env` file you created [here](#41-env-setup).

```bash
export REDIS_HOST=<host> # with format <host>, without protocol (es: queue - as per the name in the docker compose)
export REDIS_PORT=<port>
```

### 4.2 How to use it

You always want to use the interface in your code, not the actual implementation of a specific provider, so that you can benefit from this abstraction layer, without the need to change the code as the provider changes.<br>
Here a code snipped for the import.

```python
# You choose whether to use get_vector_db or get_vector_db_ctx, based on your needs
from dos_utility.vector_db import VectorDBInterface, ObjectData, SemanticSearchResult, get_vector_db_ctx, get_vector_db, IndexCreationException, IndexDeletionException, PutObjectsException, DeleteObjectsException
```

In order to have better understanding of each element, checkout [queue.md](./queue/queue.md) to see examples and [queue_interface.md](./queue/queue_interface.md) to find out what methods are available for the interface.

### 4.3 Implement new provider

If you want to provide a new implementation for a different provider you are welcome, just make sure to respect some standards:

- create a class which implements the `VectorDBInterface` ([here](./vector_db/vector_db_interface.md) the specs), under `src/dos_utility/vector_db/interface.py`. Write your own code in a dedicated folder under `src/dos_utility/vector_db` module.
- update the `get_vector_db_ctx` with your new implementation, under `src/dos_utility/vector_db/__init__.py`.
- write unit tests for your new implementation and for the updated `get_vector_db_ctx`.
- update this doc so that the documentation is up to date.

### 2.4 Update the interface

It could be possible that the actual interface doesn't cover some needed behaviors or some vendors functionalities. If you want to update it you can do it, but be sure to align all pre-existing provider implementations and update unit-tests. Other than that, check each micro-service which use that interface and make sure it doesn't break with the new structure.

