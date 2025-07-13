#!/bin/bash
# Auto backup completo - Mailton Kanazo
# Ubicación: /opt/mailton/scripts/auto_backup.sh
# Versión mejorada que incluye todo el proyecto

DATE=$(date +%Y%m%d_%H%M%S)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"  # /opt/mailton
BACKUP_DIR="$PROJECT_DIR/backups"

echo "🔄 Iniciando backup automático completo: $DATE"
echo "📁 Proyecto: $PROJECT_DIR"
echo "📄 Script: $SCRIPT_DIR/$(basename "$0")"

# Verificar que estamos en el directorio correcto
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Directorio del proyecto no encontrado: $PROJECT_DIR"
    exit 1
fi

cd $PROJECT_DIR

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

echo "📦 Creando backup físico completo..."

# Backup físico COMPLETO del proyecto (excluyendo archivos innecesarios)
tar -czf $BACKUP_DIR/mailton-full-backup_$DATE.tar.gz \
    --exclude='backups' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='*.log' \
    --exclude='.wwebjs_cache' \
    backend/ whatsapp/ scripts/ docs/ *.md 2>/dev/null

# Backup específico de configuraciones críticas
echo "⚙️ Backup de configuraciones críticas..."
tar -czf $BACKUP_DIR/config-backup_$DATE.tar.gz \
    backend/app/ \
    whatsapp/index.js \
    whatsapp/package.json \
    scripts/ \
    docs/ \
    roadmap_actualizado_micro_fases.md 2>/dev/null

# Backup de PM2 (si existe)
if command -v pm2 &> /dev/null; then
    echo "🔧 Backup de configuración PM2..."
    pm2 save &>/dev/null
    if [ -f ~/.pm2/dump.pm2 ]; then
        cp ~/.pm2/dump.pm2 $BACKUP_DIR/pm2-config_$DATE.json
    fi
fi

# Backup de autenticación WhatsApp (si existe)
if [ -d "whatsapp/.wwebjs_auth" ]; then
    echo "📱 Backup de autenticación WhatsApp..."
    tar -czf $BACKUP_DIR/whatsapp-auth_$DATE.tar.gz whatsapp/.wwebjs_auth 2>/dev/null
fi

echo "📊 Información del backup:"
ls -lah $BACKUP_DIR/mailton-full-backup_$DATE.tar.gz
ls -lah $BACKUP_DIR/config-backup_$DATE.tar.gz

# Backup git (solo si hay cambios)
echo "📝 Verificando cambios para Git..."

# Verificar si estamos en un repo git
if [ -d ".git" ]; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
    
    # Verificar cambios
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "🔄 Detectados cambios, haciendo commit automático..."
        git add -A
        git commit -m "auto: backup automático $DATE

- Backup físico: mailton-full-backup_$DATE.tar.gz
- Configuraciones: config-backup_$DATE.tar.gz
- Estado del sistema al: $(date)
- Branch: $BRANCH"
        
        # Push con manejo de errores
        if git push origin $BRANCH 2>/dev/null; then
            echo "✅ Backup git completado: push a $BRANCH"
        else
            echo "⚠️ Warning: No se pudo hacer push (posible problema de conectividad)"
        fi
    else
        echo "ℹ️ Sin cambios para backup git"
    fi
else
    echo "⚠️ Warning: No es un repositorio git"
fi

# Limpiar backups antiguos (mantener últimos 10)
echo "🧹 Limpiando backups antiguos..."
find $BACKUP_DIR -name "mailton-full-backup_*.tar.gz" -type f | sort -r | tail -n +11 | xargs rm -f 2>/dev/null
find $BACKUP_DIR -name "config-backup_*.tar.gz" -type f | sort -r | tail -n +11 | xargs rm -f 2>/dev/null

# Resumen final
echo ""
echo "✅ BACKUP COMPLETADO: $DATE"
echo "📦 Archivos generados:"
echo "   - mailton-full-backup_$DATE.tar.gz (proyecto completo)"
echo "   - config-backup_$DATE.tar.gz (configuraciones críticas)"
[ -f "$BACKUP_DIR/pm2-config_$DATE.json" ] && echo "   - pm2-config_$DATE.json (configuración PM2)"
[ -f "$BACKUP_DIR/whatsapp-auth_$DATE.tar.gz" ] && echo "   - whatsapp-auth_$DATE.tar.gz (autenticación WhatsApp)"
echo ""
echo "📁 Ubicación: $BACKUP_DIR"
echo "💾 Espacio usado: $(du -sh $BACKUP_DIR | cut -f1)"
