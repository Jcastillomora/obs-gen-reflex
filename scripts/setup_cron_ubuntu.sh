#!/bin/bash
# ============================================================================
# setup_cron_ubuntu.sh
# --------------------
# Script para configurar el cron job semanal en Ubuntu/Linux.
# Agrega una entrada al crontab para ejecutar el sync cada viernes a las 2 AM.
#
# Uso:
#     bash scripts/setup_cron_ubuntu.sh
# ============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Obtener rutas absolutas
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SYNC_SCRIPT="$SCRIPT_DIR/run_weekly_sync.sh"
LOG_FILE="/var/log/ocde_sync.log"

echo -e "${GREEN}========================================================================${NC}"
echo -e "${GREEN}OCDE - Configuración de Sync Semanal${NC}"
echo -e "${GREEN}========================================================================${NC}"
echo ""

# Verificar que existe el script
if [ ! -f "$SYNC_SCRIPT" ]; then
    echo -e "${RED}[ERROR] No se encontró el script: $SYNC_SCRIPT${NC}"
    exit 1
fi

# Hacer el script ejecutable
echo -e "${YELLOW}[1/4] Haciendo el script ejecutable...${NC}"
chmod +x "$SYNC_SCRIPT"
echo -e "${GREEN}      OK${NC}"

# Verificar permisos de log
echo -e "${YELLOW}[2/4] Verificando permisos de log...${NC}"
if [ ! -f "$LOG_FILE" ]; then
    echo "      Creando archivo de log: $LOG_FILE"
    sudo touch "$LOG_FILE"
    sudo chown $USER:$USER "$LOG_FILE"
fi
echo -e "${GREEN}      OK${NC}"

# Crear entrada de cron
CRON_ENTRY="0 2 * * 5 $SYNC_SCRIPT >> $LOG_FILE 2>&1"

echo -e "${YELLOW}[3/4] Verificando crontab actual...${NC}"
if crontab -l 2>/dev/null | grep -F "$SYNC_SCRIPT" > /dev/null; then
    echo -e "${YELLOW}      Ya existe una entrada para este script en crontab${NC}"
    echo ""
    echo "Entrada actual:"
    crontab -l | grep -F "$SYNC_SCRIPT"
    echo ""
    read -p "¿Deseas reemplazarla? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Cancelado por el usuario${NC}"
        exit 0
    fi
    # Eliminar entrada existente
    crontab -l | grep -v -F "$SYNC_SCRIPT" | crontab -
fi

# Agregar nueva entrada
echo -e "${YELLOW}[4/4] Agregando entrada a crontab...${NC}"
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
echo -e "${GREEN}      OK${NC}"

echo ""
echo -e "${GREEN}========================================================================${NC}"
echo -e "${GREEN}Configuración completada exitosamente${NC}"
echo -e "${GREEN}========================================================================${NC}"
echo ""
echo "Resumen de la configuración:"
echo "  Script:    $SYNC_SCRIPT"
echo "  Horario:   Cada viernes a las 2:00 AM"
echo "  Log:       $LOG_FILE"
echo ""
echo "Entrada cron agregada:"
echo "  $CRON_ENTRY"
echo ""
echo "Comandos útiles:"
echo "  - Ver crontab:        crontab -l"
echo "  - Editar crontab:     crontab -e"
echo "  - Ver log:            tail -f $LOG_FILE"
echo "  - Ejecutar manual:    bash $SYNC_SCRIPT"
echo ""
echo -e "${YELLOW}NOTA: El primer sync automático será el próximo viernes a las 2:00 AM${NC}"
echo ""
