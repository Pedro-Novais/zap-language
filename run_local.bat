@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Subindo aplicacao Zap-Language...
python worker_run.py
pause