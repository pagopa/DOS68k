# Build project

The following guide is intended to be used to setup up the whole project, or a single service of it.<br>
For an overview of all available services, see the [project README](../README.md#services).

> **Note:** Several services depend on the shared [dos-utility](../dos-utility/README.md) package, which provides common abstractions for auth, queue, storage, and database layers. This package is referenced by services and installed automatically as a local dependency — you do not need to install it manually.

## 1. Env files

First of all, make sure you have all the `.env` required files. For each service you want to start, check whether its folder contains a `.env.template` file:

- **If a `.env.template` exists**: copy it to `.env` in the same folder and fill in the required values. Instructions for each variable are provided as comments inside the template.
- **If no `.env.template` exists**: the service requires no environment configuration and no `.env` file needs to be created.

Also make sure even external services (eg. localstack/langfuse/minio/ecc...) have their own .env file. Look at the `compose.yaml` and the `./.env.*.template` at the root folder of the project.

## 2. Specific service configurations

For each service take a look at the respective `README.md` file, which could give you instructions on how to configure, if needed, the service before starting it.

## 3. Docker compose

### 3.1 Whole project

> Make sure you didn't skip the [env](#1-env-files) setup.

At the root level of the repo there are two docker compose files:
- **compose.yaml:** build containers from source code.
- **compose-remote.yaml:** start containers pulling public built images from ghcr.

```bash
docker compose up -d --build
# docker compose -f compose-remote.yaml up -d
```
