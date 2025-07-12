#!/bin/bash
# Auto backup con git y archivos
cd /opt/mailton/backend

DATE=$(date +%Y%m%d_%H%M%S)
BRANCH=$(git branch --show-current)

echo "🔄 Iniciando backup automático: $DATE"

# Crear directorio de backups si no existe
mkdir -p /opt/mailton/backups

# Backup físico de archivos
tar -czf /opt/mailton/backups/backup_$DATE.tar.gz /opt/mailton/backend/app --exclude='__pycache__'

# Backup git (solo si hay cambios)
if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A
    git commit -m "auto: backup automático $DATE"
    git push origin $BRANCH
    echo "✅ Backup git completado: $DATE"
else
    echo "ℹ️ Sin cambios para backup: $DATE"
fi

echo "✅ Backup físico guardado: backup_$DATE.tar.gz"
