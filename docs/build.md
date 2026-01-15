# Build project

The following guide is intended to be used to setup up the whole project, or a single service of it.<br>

## 1. Env files

First of all, make sure you have all the .env required files. To create those choose the service you want to start (or all of them). Whitin its folder there is a (or more than one) `**.env.template` that you must use to create your own `**.env`. You can find instructions about variables within the `.env.template`, if needed.<br>

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