#!/bin/bash
# 🚀 Ver logs en tiempo real del backend IA y del gateway WhatsApp
# Requiere multitail instalado (sudo apt install multitail)

if command -v multitail &> /dev/null
then
    multitail -l "pm2 logs mailton-backend --lines 100" -l "pm2 logs mailton-whatsapp --lines 100"
else
    echo "multitail no está instalado. Usando tail por separado."
    gnome-terminal -- bash -c "pm2 logs mailton-backend --lines 100"
    gnome-terminal -- bash -c "pm2 logs mailton-whatsapp --lines 100"
fi
