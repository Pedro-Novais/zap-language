@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Subindo API zap language...
python app.py
pause