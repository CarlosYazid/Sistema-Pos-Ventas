# / -- base image -- /
FROM python:3.13-slim AS base

RUN apt-get update

# configs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# / -- builder image -- /
FROM base AS builder

# uv configs
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# git
RUN apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# uv
RUN pip install --no-cache-dir uv
ENV PATH="/root/.local/bin:/app/.venv/bin:$PATH"

# deps metadata
COPY pyproject.toml uv.lock* ./

# / ----------------------- Api ----------------------- /

# / -- dev builder -- /
FROM builder AS builder-api-dev
RUN uv sync --frozen --group api --group dev --group back-task

# / -- prod builder -- /
FROM builder AS builder-api-prod
RUN uv sync --no-dev --no-install-project --group api --group back-task

# / -- dev image -- /
FROM base AS api-dev

RUN apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libffi8 \
        libgdk-pixbuf-2.0-0 \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder-api-dev /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY src src

ARG PORT=8080

EXPOSE ${PORT}

# / -- prod image -- /
FROM base AS api-prod

RUN apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libffi8 \
        libgdk-pixbuf-2.0-0 \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# no-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder-api-prod /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=appuser:appgroup src src

COPY --chown=appuser:appgroup alembic.ini .

COPY --chown=appuser:appgroup migrations migrations

ARG PORT=8000

EXPOSE ${PORT}

USER appuser

# / ----------------------- Back-Task ----------------------- /

# / -- dev builder -- /
FROM builder AS builder-back-task-dev
RUN uv sync --frozen --group back-task --group dev

# / -- prod builder -- /
FROM builder AS builder-back-task-prod
RUN uv sync --no-dev --no-install-project --group back-task

# / -- dev image -- /
FROM base AS back-task-dev

# WeasyPrint deps
RUN apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libffi8 \
        libgdk-pixbuf-2.0-0 \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder-back-task-dev /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy necessary modules
COPY src/celery_app.py src/

COPY src/tasks src/tasks/

COPY src/core/settings.py src/core/storage.py src/core/observability.py src/core/

COPY src/services/email.py src/services/

COPY src/models/ src/models/

COPY src/utils/order.py src/utils/

COPY src/templates/ src/templates/

# / -- prod image -- /
FROM base AS back-task-prod

# WeasyPrint deps
RUN apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libffi8 \
        libgdk-pixbuf-2.0-0 \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder-back-task-prod /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# no-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy necessary modules
COPY --chown=appuser:appgroup src/celery_app.py src/

COPY --chown=appuser:appgroup src/tasks/ src/tasks/

COPY --chown=appuser:appgroup src/core/settings.py src/core/storage.py src/core/observability.py src/core/

COPY --chown=appuser:appgroup src/models/ src/models/

COPY --chown=appuser:appgroup src/utils/order.py src/utils/

COPY --chown=appuser:appgroup src/templates/ src/templates/

USER appuser
