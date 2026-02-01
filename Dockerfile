FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY . .

RUN echo '#!/bin/bash\n\
flask db upgrade\n\
celery -A external.services.celery worker --loglevel=info --pool=solo &\n\
gunicorn --bind 0.0.0.0:$PORT app:app' > /app/start.sh

RUN chmod +x /app/start.sh

# 8. Comando de entrada
CMD ["/app/start.sh"]