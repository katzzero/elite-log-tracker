@echo off
echo ================================================
echo Elite Dangerous Log Tracker - Instalador
echo ================================================
echo.
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.8 ou superior em: https://python.org
    pause
    exit /b 1
)

echo.
echo Instalando dependencias...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Instalacao concluida com sucesso!
echo ================================================
echo.
echo Para iniciar o aplicativo, execute: python app.py
echo.
pause
