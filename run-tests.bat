@echo off

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Rodando testes unitarios...
call pytest --cov=core/interactor --cov-report=term-missing test

pause