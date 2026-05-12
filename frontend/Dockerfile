# Stage 1: Build the React app
FROM node:22-alpine AS build

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable

ENV VITE_API_BASE_URL=__API_BASE_URL__

WORKDIR /app

COPY ./frontend .
RUN pnpm install --ignore-scripts && pnpm rebuild esbuild && pnpm build

# Stage 2: Nginx
FROM nginx:1.25.4-alpine3.18

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
