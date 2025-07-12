#!/bin/bash

# Configuración inicial
BASE_DIR="/opt/mailton"
LOG_FILE="$BASE_DIR/scripts/permissions_log.txt"
OWNER="secureadmin"

echo "🔍 Iniciando verificación de permisos y propietarios en $BASE_DIR"
echo "🕒 $(date)" > "$LOG_FILE"

# Permisos recomendados
DIR_PERM="755"
PY_FILE_PERM="644"
SH_FILE_PERM="755"

# 1. Verificar y corregir propietarios
echo "🔧 Corrigiendo propietarios..." >> "$LOG_FILE"
chown -R $OWNER:$OWNER "$BASE_DIR"
echo "✅ Todos los archivos ahora pertenecen a: $OWNER" >> "$LOG_FILE"

# 2. Directorios - permisos 755
find "$BASE_DIR" -type d | while read -r dir; do
  perm=$(stat -c "%a" "$dir")
  if [ "$perm" != "$DIR_PERM" ]; then
    chmod "$DIR_PERM" "$dir"
    echo "🔧 Directorio corregido: $dir (was $perm)" >> "$LOG_FILE"
  fi
done

# 3. Archivos .py - permisos 644
find "$BASE_DIR" -type f -name "*.py" | while read -r pyfile; do
  perm=$(stat -c "%a" "$pyfile")
  if [ "$perm" != "$PY_FILE_PERM" ]; then
    chmod "$PY_FILE_PERM" "$pyfile"
    echo "🔧 Archivo Python corregido: $pyfile (was $perm)" >> "$LOG_FILE"
  fi
done

# 4. Archivos .sh - permisos 755
find "$BASE_DIR" -type f -name "*.sh" | while read -r shfile; do
  perm=$(stat -c "%a" "$shfile")
  if [ "$perm" != "$SH_FILE_PERM" ]; then
    chmod "$SH_FILE_PERM" "$shfile"
    echo "🔧 Script corregido: $shfile (was $perm)" >> "$LOG_FILE"
  fi
done

echo "✅ Verificación y corrección finalizadas con éxito."
echo "📝 Revisa el log: $LOG_FILE"
