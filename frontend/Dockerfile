# Frontend Dockerfile for Project RawHorse
# Multi-stage build for React/Vite application

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --no-audit --no-fund

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Output
# Just copy built files to a volume for Caddy to serve
FROM alpine:latest

# Create output directory
RUN mkdir -p /usr/share/caddy

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/caddy

# The frontend container just provides the built files
# Caddy will serve them via the shared volume
CMD ["echo", "Frontend built successfully"]
