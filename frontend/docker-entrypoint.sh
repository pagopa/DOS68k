#!/bin/sh
set -e

sed -i "s|__API_BASE_URL__|${VITE_API_BASE_URL}|g" /usr/share/nginx/html/assets/*.js

exec nginx -g "daemon off;"
