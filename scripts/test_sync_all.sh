#!/bin/bash
# Script para probar sincronizacion semanal completa (Linux/Ubuntu)
# Ejecuta en modo DRY RUN (sin modificar archivos)

echo "======================================"
echo "PRUEBA DE SINCRONIZACION COMPLETA"
echo "======================================"
echo ""
echo "Este script ejecuta el sync completo en modo PRUEBA (--dry-run)"
echo "NO se modificaran archivos, solo se mostrara que se haria"
echo ""
echo "Pasos:"
echo "  1. Scraping de proyectos.xlsx (SALTADO en dry-run)"
echo "  2. Sincronizacion de proyectos_total.xlsx (simulado)"
echo "  3. Sincronizacion de publicaciones_total.xlsx (simulado)"
echo ""
read -p "Presiona ENTER para continuar..."

cd "$(dirname "$0")/.."
python scripts/run_weekly_sync_all.py --delay 0.5 --dry-run

echo ""
echo "======================================"
echo "PRUEBA COMPLETADA"
echo "======================================"
echo ""
echo "Para ejecutar el sync REAL (modificando archivos):"
echo "  python scripts/run_weekly_sync_all.py"
echo ""
