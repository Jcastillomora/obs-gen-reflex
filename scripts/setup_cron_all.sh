#!/bin/bash
# Configurar cron job para sincronizacion semanal completa (Linux/Ubuntu)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SYNC_SCRIPT="$SCRIPT_DIR/run_weekly_sync_all.sh"
LOG_FILE="/var/log/ocde_sync_all.log"

echo "======================================================================"
echo "CONFIGURACION DE CRON JOB - SINCRONIZACION SEMANAL COMPLETA"
echo "======================================================================"
echo ""
echo "Este script configurara un cron job para ejecutar:"
echo "  $SYNC_SCRIPT"
echo ""
echo "Programacion: Todos los viernes a las 2:00 AM"
echo "Log: $LOG_FILE"
echo ""
read -p "Continuar? (s/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Cancelado por el usuario"
    exit 1
fi

# Dar permisos de ejecucion
chmod +x "$SYNC_SCRIPT"
echo "[OK] Permisos de ejecucion otorgados"

# Crear log file si no existe
sudo touch "$LOG_FILE"
sudo chmod 666 "$LOG_FILE"
echo "[OK] Archivo de log creado"

# Agregar cron job
CRON_LINE="0 2 * * 5 $SYNC_SCRIPT >> $LOG_FILE 2>&1"

# Verificar si ya existe
if crontab -l 2>/dev/null | grep -F "$SYNC_SCRIPT" > /dev/null; then
    echo "[WARN] El cron job ya existe. Eliminando entrada anterior..."
    crontab -l 2>/dev/null | grep -v -F "$SYNC_SCRIPT" | crontab -
fi

# Agregar nueva entrada
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
echo "[OK] Cron job agregado exitosamente"

echo ""
echo "======================================================================"
echo "CONFIGURACION COMPLETADA"
echo "======================================================================"
echo ""
echo "Cron job configurado:"
echo "  $CRON_LINE"
echo ""
echo "Para verificar:"
echo "  crontab -l"
echo ""
echo "Para monitorear el log:"
echo "  tail -f $LOG_FILE"
echo ""
