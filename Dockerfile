FROM python:3.10-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY pyproject.toml .
RUN pip install .

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
COPY pyproject.toml .

# Expose port
EXPOSE 8000

# Run migrations, seed database, and start application
CMD ["sh", "-c", "alembic upgrade head && python -m scripts.seed && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
