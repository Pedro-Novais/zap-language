@echo off

echo Ativando ambiente virtual...
call venv\Scripts\activate

@REM echo Criando schema do banco...
@REM python -m external.database.scripts.create_schema

@REM echo Criando tabelas...
@REM python -m external.database.scripts.create_tables

echo Subindo aplicacao...
python app.py
pause
