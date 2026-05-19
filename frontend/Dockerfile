# Stage 1: Build the React app
FROM node:22-alpine@sha256:8ea2348b068a9544dae7317b4f3aafcdc032df1647bb7d768a05a5cad1a7683f AS build

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable

ENV VITE_API_BASE_URL=__API_BASE_URL__

WORKDIR /app

COPY ./frontend .
RUN pnpm install --ignore-scripts && pnpm rebuild esbuild && pnpm build

# Stage 2: Nginx
FROM nginx:1.25.4-alpine3.18@sha256:31bad00311cb5eeb8a6648beadcf67277a175da89989f14727420a80e2e76742

# Rimuove config di default
RUN rm /etc/nginx/conf.d/default.conf

# Copia config custom
COPY ./frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copia build nella directory corretta
COPY --from=build /app/dist /usr/share/nginx/html/

COPY ./frontend/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/docker-entrypoint.sh"]
