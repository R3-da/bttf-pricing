FROM python:3.10-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y build-essential python3-dev && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip poetry==2.3.1 poetry-plugin-export
COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --without-hashes -o requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV PYTHONPATH=/app

COPY src ./src
COPY static ./static
COPY scripts ./scripts
COPY migrations ./migrations
COPY alembic.ini .

# Expose port
EXPOSE 8000

# Run migrations, seed database, and start application
CMD ["sh", "-c", "(alembic upgrade head || echo 'Migrations failed') && (python -m scripts.seed || echo 'Seeding failed') && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
