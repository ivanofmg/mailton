#!/bin/bash
cd /opt/mailton/backend

echo "📝 Generando CHANGELOG..."

# Header del changelog
cat > CHANGELOG.md << EOF
# CHANGELOG - Mailton Kanazo MVP

Todas las funcionalidades y cambios importantes del proyecto.

## $(date +%Y-%m-%d) - Versión Actual

EOF

# Agregar commits recientes
echo "### Cambios recientes:" >> CHANGELOG.md
git log --oneline --pretty=format:"- %s" -10 >> CHANGELOG.md
echo "" >> CHANGELOG.md

# Copiar a docs
cp CHANGELOG.md /opt/mailton/docs/CHANGELOG.md 2>/dev/null || true

echo "✅ CHANGELOG actualizado"
