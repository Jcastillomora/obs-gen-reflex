#!/bin/bash
# Script para ejecutar la sincronización de publicaciones dentro del contenedor Docker
# Uso:
#   bash scripts/docker_sync.sh           # Ejecuta el sync real
#   bash scripts/docker_sync.sh --dry-run # Simula el sync sin modificar archivos

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "==========================================="
echo "  Sync de Publicaciones (Docker)"
echo "==========================================="
echo ""
echo "Ejecutando sync dentro del contenedor..."
echo ""

# Pasar todos los argumentos al script de Python dentro del contenedor
docker compose exec app python scripts/sync_publicaciones_to_db.py "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✓ Sync completado exitosamente"
    echo ""
    echo "Para ver el archivo generado:"
    echo "  cat OCDE/.last_sync.json"
    echo ""
    echo "Los cambios se aplicarán automáticamente (el contenedor está montando el archivo)."
else
    echo ""
    echo "✗ Error en el sync (exit code: $EXIT_CODE)"
    exit $EXIT_CODE
fi
