#!/bin/bash
# Script para ejecutar sincronizacion semanal completa (Linux/Ubuntu)
# Proyectos + Publicaciones
#
# Usar en cron:
#   0 2 * * 5 /ruta/completa/OCDE/scripts/run_weekly_sync_all.sh >> /var/log/ocde_sync.log 2>&1

echo "======================================================================"
echo "SINCRONIZACION SEMANAL COMPLETA - OCDE"
echo "======================================================================"
date

cd "$(dirname "$0")/.."

# Ejecutar sincronizacion completa
python scripts/run_weekly_sync_all.py --delay 1.5

echo ""
echo "======================================================================"
echo "SINCRONIZACION COMPLETADA"
echo "======================================================================"
date
