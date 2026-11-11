# PISMANIYE — Hardened Cloud Run & Container Production Image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    PISMANIYE_MODE=local_deterministic \
    PISMANIYE_HOST=0.0.0.0 \
    PISMANIYE_PORT=8080

WORKDIR /app

# Create non-root system user for container security
RUN groupadd --gid 10001 pismaniye && \
    useradd --uid 10001 --gid pismaniye --shell /bin/false --create-home pismaniye

COPY pyproject.toml README.md ./
COPY pismaniye ./pismaniye

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --no-build-isolation -e . && \
    mkdir -p /app/.pismaniye_state && \
    chown -R pismaniye:pismaniye /app

USER pismaniye

EXPOSE 8080

CMD ["uvicorn", "pismaniye.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
