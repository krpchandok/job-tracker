FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY services/scraper/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/scraper/ .
RUN chown -R appuser:appuser /app

USER appuser

CMD ["python", "main.py"]