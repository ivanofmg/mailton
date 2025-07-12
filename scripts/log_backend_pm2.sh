#!/bin/bash

LOG_FILE="/var/log/mailton_backend.log"

# Asegura que el archivo existe y es editable por el usuario actual
sudo touch $LOG_FILE
sudo chown $USER:$USER $LOG_FILE

echo "📝 Guardando logs en tiempo real de mailton-backend a $LOG_FILE ..."
echo "Presiona Ctrl+C para detener el monitoreo en esta sesión."

# Inicia logeo continuo
pm2 logs mailton-backend --lines 100 >> $LOG_FILE
