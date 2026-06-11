# Web Frontend Dockerfile
# Multi-stage build for minimal image size

# Build stage
FROM node:22-slim AS build

WORKDIR /app

ENV VITE_KEEP_OWN_DOMAIN=true

# Copy the workspace root package files
COPY web/package.json web/package-lock.json ./

# Copy all workspace packages
COPY web/packages ./packages
COPY web/apps ./apps

# Install dependencies at the workspace root
RUN npm ci

WORKDIR /app/packages/api
RUN npm run build

# Build the specific app
WORKDIR /app/apps/dev-observer
RUN npm run build

# Production stage
FROM node:22-slim AS production

WORKDIR /app

ENV VITE_KEEP_OWN_DOMAIN=true
# Install a lightweight HTTP server
RUN npm install -g serve

# Copy built files from build stage
COPY --from=build /app/apps/dev-observer/dist /app/dist

# Expose port for the application
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production

# Start the server
CMD ["serve", "-s", "dist", "-l", "3000"]
