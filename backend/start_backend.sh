#!/bin/bash

echo "🚀 Iniciando backend FastAPI de Mailton Kanazo..."
cd /opt/mailton/backend || exit
source venv/bin/activate
python3 start.py
