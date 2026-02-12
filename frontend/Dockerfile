# Stage 1: Build the React app
FROM node:20-alpine@sha256:09e2b3d9726018aecf269bd35325f46bf75046a643a66d28360ec71132750ec8 AS build

WORKDIR /app

COPY ./frontend/package.json ./frontend/package-lock.json* ./
RUN npm install

COPY ./frontend .
RUN npm run build


# Stage 2: Nginx
FROM nginx:1.25.4-alpine3.18@sha256:31bad00311cb5eeb8a6648beadcf67277a175da89989f14727420a80e2e76742

# Rimuove config di default
RUN rm /etc/nginx/conf.d/default.conf

# Copia config custom
COPY ./frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copia build nella directory corretta
COPY --from=build /app/dist /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
