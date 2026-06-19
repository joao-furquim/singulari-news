# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
# Use npm install instead of npm ci so npm resolves platform-specific
# binaries (esbuild, etc.) for linux/x64 inside Docker, regardless of
# the OS that generated the package-lock.json.
RUN npm cache clean --force && npm install --legacy-peer-deps
COPY . .
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
