@echo off
echo [1/3] Ativando ambiente virtual...
call venv\Scripts\activate

echo [2/3] Gerando arquivo de migracao...
set /p msg="Digite a descricao da migracao: "
flask db migrate -m "%msg%"

set /p verifying="Verificando arquivo de migracao..."
echo [3/3] Aplicando alteracoes no banco de dados...
flask db upgrade

echo.
echo Operacao concluida com sucesso!
pause