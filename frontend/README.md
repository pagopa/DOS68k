# Frontend

This frontend app is not intended to be a fully and stable UI for the chatbot. It's just a support for those who want to have a visual helper about the core chatbot service.

## Prerequisites

In order to work locally with this service you need the following softwares:

- pnpm/npm
- docker

## Start service

If you want to independently start this service, run the following commands.

```bash
cd .. # Make sure to be at the root level of the repo
docker compose up -d --build frontend
```

Now you can access the web page at `http://localhost:80`.
There is also a `/health` page which gives you the health status of the backend services this web page is going to interact with. In order to se it functioning, you have to start those services as well through the docker compose. You can check infos about them in the `README.md` under the respective folder.
