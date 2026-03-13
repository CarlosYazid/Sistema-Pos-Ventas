# / -- base image -- /
FROM python:3.12-slim AS base

# configs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# / -- builder image -- /
FROM base AS builder

ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# uv
RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# core deps
COPY pyproject.toml uv.lock* ./

# install deps with uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --compile-bytecode
    
# / -- runtime image -- /
FROM base AS runtime

# deps
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

# core backend
COPY src ./src

EXPOSE 8080
