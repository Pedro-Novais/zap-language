@echo off

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Rodando celery
celery -A external.services.celery worker --loglevel=info --pool=solo &
pause