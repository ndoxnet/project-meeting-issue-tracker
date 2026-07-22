# Concept by MrHan (08974747477)
# Frontend image — Project Meeting Issue Tracker
#
# >>> IMPORTANT: Frontend image must be built OUTSIDE the production VPS. <<<
# The build stage runs `npm install` + `vite build`, which can spike >1 GB RAM.
# On the resource-constrained production VPS this risks OOM-killing co-located
# services. Build on a developer machine or CI and push the image to a registry;
# the VPS only pulls the runtime image. (See ADR-004.)

# ---- Build stage (runs off-VPS) ----
FROM node:20-alpine AS build
WORKDIR /app
# Install from the committed lockfile for reproducible builds. The lockfile is
# generated off-VPS (`npm install`) and committed — `npm ci` requires it.
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# `npm run build` = `tsc -b && vite build` (typecheck then bundle). The committed
# generated API types (src/api/generated/schema.ts) must be current — verify with
# `npm run check:api` in CI before building. No production sourcemaps.
RUN npm run build

# ---- Runtime stage (Nginx, non-root) ----
FROM nginx:1.27-alpine AS runtime

# Serve on 8080 as non-root.
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist /usr/share/nginx/html

# Prepare writable temp dirs and hand ownership to the unprivileged nginx user.
RUN mkdir -p /tmp/client_temp /tmp/proxy_temp /tmp/fastcgi_temp \
        /tmp/uwsgi_temp /tmp/scgi_temp \
    && chown -R nginx:nginx /usr/share/nginx/html /tmp/*_temp
USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
