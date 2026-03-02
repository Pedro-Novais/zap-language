@echo off

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Rodando testes unitarios...
call pytest --cov=core --cov-report=term-missing test

pause