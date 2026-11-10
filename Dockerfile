
FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync --frozen --no-dev

COPY api.py app.py ./

ENV PATH="/app/.venv/bin:$PATH"
