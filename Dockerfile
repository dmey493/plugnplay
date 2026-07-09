# Plug N Play — Next.js app + the Python PDF engine in one image.
# The two /api/generate-* routes shell out to Python (engine/), so the host
# must have both Node and Python. Deploy this on any Docker-capable host
# (Render, Railway, Fly.io, a VPS). Vercel's default Node runtime can't run
# the Python engine, so use a container host for full PDF support.

FROM node:22-bookworm-slim

# Python 3 for the PDF engine (fpdf2 + drawsvg).
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install JS deps first (better layer caching). Needs dev deps to build.
COPY package.json package-lock.json ./
RUN npm ci

# Install Python deps for the engine. Debian's pip is "externally managed"
# (PEP 668), so allow a system install inside this container.
COPY requirements.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# App source (includes engine/ and content/).
COPY . .

# Build the production Next.js bundle.
RUN npm run build

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# The API routes read PYTHON_PATH; on Linux the interpreter is `python3`.
ENV PYTHON_PATH=python3
ENV PORT=3000
EXPOSE 3000

CMD ["npm", "run", "start"]
