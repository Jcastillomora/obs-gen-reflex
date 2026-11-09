#!/bin/bash
# Script para configurar el cron semanal de sincronización de publicaciones en producción (Docker)
# Este script debe ejecutarse EN EL SERVIDOR DE PRODUCCIÓN

set -e

CRON_USER=$(whoami)
PROJECT_DIR="$HOME/obs-gen-reflex"
LOG_FILE="/var/log/ocde_sync.log"

echo "==========================================="
echo "  Configurar Cron Semanal (Docker)"
echo "==========================================="
echo ""
echo "Usuario: $CRON_USER"
echo "Directorio del proyecto: $PROJECT_DIR"
echo "Log: $LOG_FILE"
echo ""

# Crear el archivo de log si no existe
sudo touch "$LOG_FILE"
sudo chown "$CRON_USER:$CRON_USER" "$LOG_FILE"

# Crear entrada de cron
CRON_COMMAND="0 2 * * 5 cd $PROJECT_DIR && docker compose exec -T app python scripts/sync_publicaciones_to_db.py >> $LOG_FILE 2>&1"

echo "Se agregará la siguiente entrada al crontab:"
echo ""
echo "$CRON_COMMAND"
echo ""
echo "Esto ejecutará el sync cada viernes a las 2:00 AM."
echo ""

read -p "¿Continuar? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelado."
    exit 0
fi

# Verificar si ya existe una entrada similar
if crontab -l 2>/dev/null | grep -q "sync_publicaciones_to_db.py"; then
    echo "⚠ Ya existe una entrada de sync en el crontab."
    echo "Contenido actual del crontab:"
    echo ""
    crontab -l | grep "sync_publicaciones_to_db.py" || true
    echo ""
    read -p "¿Reemplazar la entrada existente? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Eliminar entradas antiguas
        crontab -l | grep -v "sync_publicaciones_to_db.py" | crontab -
        echo "✓ Entrada antigua eliminada"
    else
        echo "Cancelado."
        exit 0
    fi
fi

# Agregar nueva entrada
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

echo ""
echo "✓ Cron configurado exitosamente"
echo ""
echo "Verificación del crontab:"
crontab -l | grep "sync_publicaciones_to_db.py" || true
echo ""
echo "Para ver los logs en tiempo real:"
echo "  tail -f $LOG_FILE"
echo ""
echo "Para ejecutar el sync manualmente:"
echo "  cd $PROJECT_DIR && bash scripts/docker_sync.sh"
echo ""
