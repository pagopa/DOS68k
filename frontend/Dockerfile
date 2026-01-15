# Stage 1: Build the React app
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build


# Stage 2: Nginx
FROM nginx:1.25.4-alpine3.18

# Rimuove config di default
RUN rm /etc/nginx/conf.d/default.conf

# Copia config custom
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia build nella directory corretta
COPY --from=build /app/dist /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
