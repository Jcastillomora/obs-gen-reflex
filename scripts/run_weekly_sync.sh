#!/bin/bash
# ============================================================================
# run_weekly_sync.sh
# ------------------
# Script para ejecutar el sync semanal de publicaciones en Ubuntu/Linux.
# Diseñado para ser ejecutado por cron cada viernes a las 2:00 AM.
#
# Uso manual:
#     bash scripts/run_weekly_sync.sh
#
# Configuración cron (ejecutar: crontab -e):
#     0 2 * * 5 /ruta/completa/al/proyecto/OCDE/scripts/run_weekly_sync.sh >> /var/log/ocde_sync.log 2>&1
#
# Ejemplo:
#     0 2 * * 5 /home/user/OCDE/scripts/run_weekly_sync.sh >> /var/log/ocde_sync.log 2>&1
# ============================================================================

set -e  # Salir si algún comando falla

# Obtener directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Log con timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "=========================================================================="
log "OCDE - Sync Semanal de Publicaciones"
log "=========================================================================="

# Cambiar al directorio del proyecto
cd "$PROJECT_ROOT"
log "Directorio de trabajo: $PWD"

# Verificar que existe el entorno virtual
if [ ! -f "env/bin/python" ]; then
    log "[ERROR] No se encontró el entorno virtual en env/"
    log "[ERROR] Ejecuta: python3 -m venv env && source env/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activar entorno virtual
log "Activando entorno virtual..."
source env/bin/activate

# Verificar que existe el script
if [ ! -f "scripts/sync_publicaciones_to_db.py" ]; then
    log "[ERROR] No se encontró scripts/sync_publicaciones_to_db.py"
    exit 1
fi

# Ejecutar sync con delay de 1.5s (respetuoso con el servidor)
log "Ejecutando sync de publicaciones..."
python scripts/sync_publicaciones_to_db.py --delay 1.5

EXIT_CODE=$?

# Desactivar entorno virtual
deactivate

log "=========================================================================="
if [ $EXIT_CODE -eq 0 ]; then
    log "[OK] Sync completado exitosamente"
else
    log "[ERROR] Sync falló con código $EXIT_CODE"
fi
log "=========================================================================="

exit $EXIT_CODE
