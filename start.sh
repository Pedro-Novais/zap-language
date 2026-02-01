#!/bin/bash

# 1. Roda as migrações (Sempre bom garantir que o banco tá atualizado no deploy)
flask db upgrade

# 2. Inicia o Worker do Celery em background
# Usamos o pool 'solo' ou 'gevent' se a instância for pequena (economiza RAM)
celery -A external.services.celery worker --loglevel=info --pool=solo &

# 3. Inicia o servidor Flask (Processo principal)
# Em produção, o ideal é usar o Gunicorn em vez do 'python app.py'
gunicorn --bind 0.0.0.0:$PORT app:app