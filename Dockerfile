# Deterministic build: the public service serves one same-origin FastAPI + HMI endpoint.
FROM node:22-alpine AS frontend-build
WORKDIR /build/frontend
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml README.md ./
COPY backend/ ./backend/
COPY config/ ./config/
RUN pip install --no-cache-dir .
COPY --from=frontend-build /build/frontend/dist ./frontend/dist
RUN useradd --create-home --uid 10001 tark && chown -R tark:tark /app
USER tark
EXPOSE 10000
CMD ["sh", "-c", "uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-10000}"]
