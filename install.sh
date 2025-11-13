#!/bin/bash

echo "================================================"
echo "Elite Dangerous Log Tracker - Instalador"
echo "================================================"
echo ""

echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 não encontrado!"
    echo "Instale Python 3.8 ou superior"
    exit 1
fi

python3 --version

echo ""
echo "Instalando dependências..."
echo ""

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERRO: Falha ao instalar dependências."
    exit 1
fi

echo ""
echo "================================================"
echo "Instalação concluída com sucesso!"
echo "================================================"
echo ""
echo "Para iniciar o aplicativo, execute: python3 app.py"
echo ""
