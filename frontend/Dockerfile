# Stage 1: Build the React app
FROM node:20-alpine AS build

WORKDIR /app

COPY ./frontend/package.json ./frontend/package-lock.json* ./
RUN npm install

COPY ./frontend .
RUN npm run build


# Stage 2: Nginx
FROM nginx:1.25.4-alpine3.18

# Rimuove config di default
RUN rm /etc/nginx/conf.d/default.conf

# Copia config custom
COPY ./frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copia build nella directory corretta
COPY --from=build /app/dist /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
