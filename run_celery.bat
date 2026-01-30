@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Rodando worker...
call celery -A run_worker.celery worker --loglevel=info --pool=solo
pause