@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Subindo worker zap language...
celery -A worker.run worker --loglevel=info --pool=solo
pause