@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Subindo worker zap language...
python worker_run.py
pause