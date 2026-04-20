# Build project

The following guide is intended to be used to setup up the whole project, or a single service of it.<br>
For an overview of all available services, see the [project README](../README.md#services).

> **Note:** Several services depend on the shared [dos-utility](../dos-utility/README.md) package, which provides common abstractions for auth, queue, storage, and database layers. This package is referenced by services and installed automatically as a local dependency — you do not need to install it manually.

## 1. Env files

First of all, make sure you have all the `.env` required files. For each service you want to start, check whether its folder contains a `.env.template` file:

- **If a `.env.template` exists**: copy it to `.env` in the same folder and fill in the required values. Instructions for each variable are provided as comments inside the template.
- **If no `.env.template` exists**: the service requires no environment configuration and no `.env` file needs to be created.

## 2. Specific service configurations

For each service take a look at the respective `README.md` file, which could give you instructions on how to configure, if needed, the service before starting it.

## 3. Docker compose
### 3.1 Whole project

At the root level of the repo there is the `compose.yaml` file, which contains all services that make up the project.<br>
You can start the whole project with this simple command:

```bash
docker compose up -d --build
```

If you created all the .env required files this command will spin up all the containers.<br>

### 3.2 Specific services

You can also decide to start just single services. To do so you just need to indicate the compose name of that service, like this:

```bash
docker compose up -d --build <service-name> # where <service-name> is the service name within the compose.yaml
```

You can even look at the README.md of the specific service to see the right command.
Some services has dependencies, so it could happen that, even though you specified a single service, you ended up having multiple services running.