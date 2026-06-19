# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
# Clean install resolves platform-specific binaries for linux/x64.
# --legacy-peer-deps avoids peer resolution errors across MUI packages.
RUN npm cache clean --force && rm -rf node_modules && npm install --legacy-peer-deps
COPY . .
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
