# Plug N Play — Next.js app + the Python PDF engine in one image.
# The two /api/generate-* routes shell out to Python (engine/), so the host
# must have both Node and Python. Deploy this on any Docker-capable host
# (Render, Railway, Fly.io, a VPS). Vercel's default Node runtime can't run
# the Python engine, so use a container host for full PDF support.
#
# Multi-stage: the builder installs all 1.1GB of node_modules and runs
# `next build`; the runtime stage copies only the traced standalone output
# (output: "standalone" in next.config.ts) plus engine/ + content/. Cloud Run
# cold starts pull and boot this image, so the slim runtime stage is what
# keeps first-visit latency down.

# ---- Stage 1: build the Next.js bundle ----
FROM node:22-bookworm-slim AS builder

WORKDIR /app

# Install JS deps first (better layer caching). Needs dev deps to build.
COPY package.json package-lock.json ./
RUN npm ci

# App source (includes engine/ and content/).
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ---- Stage 2: slim runtime ----
FROM node:22-bookworm-slim

# Python 3 for the PDF engine (fpdf2 + drawsvg).
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps for the engine. Debian's pip is "externally managed"
# (PEP 668), so allow a system install inside this container.
COPY requirements.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Traced server + minimal node_modules, then the assets server.js expects
# beside it (see the `output` doc: standalone omits public/ and .next/static).
COPY --from=builder /app/.next/standalone ./
# Only scripts/remove-bg.mjs (a local one-off) imports @imgly, but Turbopack's
# whole-project trace drags its ~50MB ONNX runtime into standalone anyway —
# outputFileTracingExcludes doesn't catch it. Strip it; nothing at runtime
# imports it.
RUN rm -rf ./node_modules/@imgly
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# The Python engine and content JSON are read via process.cwd() at runtime —
# spawned scripts and fs reads aren't statically traceable, so copy explicitly.
COPY --from=builder /app/engine ./engine
COPY --from=builder /app/content ./content

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# The API routes read PYTHON_PATH; on Linux the interpreter is `python3`.
ENV PYTHON_PATH=python3
# Don't hardcode PORT: container hosts like Cloud Run inject their own PORT
# (8080) and server.js binds to it. Falls back to 3000 when unset.
ENV HOSTNAME=0.0.0.0
EXPOSE 8080

# Run the standalone server directly — no npm/next CLI in the boot path.
CMD ["node", "server.js"]
