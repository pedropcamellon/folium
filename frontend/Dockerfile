# Frontend Dockerfile - Next.js with pnpm for fast builds
FROM node:20-alpine AS base

# Install pnpm globally
RUN corepack enable && corepack prepare pnpm@latest --activate

# Dependencies stage (shared by development and builder)
FROM base AS dependencies
WORKDIR /app

# Copy dependency files
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml* ./

# Install dependencies with pnpm (faster than npm)
RUN pnpm install --frozen-lockfile

# Development stage
FROM dependencies AS development

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Development command (hot reload)
CMD ["pnpm", "dev"]

# Build stage
FROM dependencies AS builder

# Copy application code
COPY . .

# Build Next.js app
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# Production stage
FROM base AS production
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built assets from builder
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/next-config-js/output
CMD ["node", "server.js"]
