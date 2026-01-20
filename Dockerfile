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

COPY src ./src
COPY static ./static
COPY pyproject.toml .

# Expose port
EXPOSE 8000

# Run commands
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
