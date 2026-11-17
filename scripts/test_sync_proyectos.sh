#!/bin/bash
# Script para probar sincronización de proyectos (Linux/macOS)
# Ejecuta el script en modo DRY RUN (sin modificar archivos)

echo "======================================"
echo "PRUEBA DE SINCRONIZACION DE PROYECTOS"
echo "======================================"
echo ""
echo "Este script ejecuta el sync en modo PRUEBA (--dry-run)"
echo "NO se modificarán archivos, solo se mostrará qué se agregaría"
echo ""
read -p "Presiona ENTER para continuar..."

cd "$(dirname "$0")/.."
python scripts/sync_proyectos_to_db.py --dry-run

echo ""
echo "======================================"
echo "PRUEBA COMPLETADA"
echo "======================================"
echo ""
echo "Para ejecutar el sync REAL (modificando archivos):"
echo "  python scripts/sync_proyectos_to_db.py"
echo ""
