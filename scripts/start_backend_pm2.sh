#!/bin/bash

echo "🚀 Iniciando backend FastAPI de Mailton Kanazo con PM2..."
cd /opt/mailton/backend || exit
source venv/bin/activate

# Detiene instancia previa si existe
pm2 delete mailton-backend > /dev/null 2>&1

# Inicia backend con PM2
pm2 start start.py --name mailton-backend --interpreter python3
