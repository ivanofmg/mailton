#!/bin/bash
echo "🚀 Iniciando gateway WhatsApp..."
cd /opt/mailton/whatsapp || exit
pm2 delete mailton-whatsapp > /dev/null 2>&1
pm2 start index.js --name mailton-whatsapp
