@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Subindo aplicacao Zao-Language...
python app.py
pause