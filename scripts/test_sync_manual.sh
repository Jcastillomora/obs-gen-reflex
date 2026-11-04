#!/bin/bash
# ============================================================================
# test_sync_manual.sh
# -------------------
# Script de prueba para ejecutar el sync de publicaciones manualmente.
# NO modifica el Excel (usa --dry-run).
#
# Uso:
#     bash scripts/test_sync_manual.sh
# ============================================================================

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Obtener directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo -e "${GREEN}========================================================================${NC}"
echo -e "${GREEN}OCDE - Test Sync Semanal de Publicaciones${NC}"
echo -e "${GREEN}========================================================================${NC}"
echo ""
echo -e "${YELLOW}Este script ejecutará el scraping en modo DRY-RUN (sin modificar Excel)${NC}"
echo -e "${YELLOW}Presiona Ctrl+C para cancelar o Enter para continuar...${NC}"
read

# Cambiar al directorio del proyecto
cd "$PROJECT_ROOT"
echo -e "${GREEN}[INFO] Directorio de trabajo: $PWD${NC}"
echo ""

# Verificar que existe el entorno virtual
if [ ! -f "env/bin/python" ]; then
    echo -e "${RED}[ERROR] No se encontró el entorno virtual en env/${NC}"
    echo -e "${RED}[ERROR] Ejecuta: python3 -m venv env${NC}"
    exit 1
fi

# Activar entorno virtual
echo -e "${GREEN}[INFO] Activando entorno virtual...${NC}"
source env/bin/activate

# Verificar que existe el script
if [ ! -f "scripts/sync_publicaciones_to_db.py" ]; then
    echo -e "${RED}[ERROR] No se encontró scripts/sync_publicaciones_to_db.py${NC}"
    exit 1
fi

# Ejecutar sync en modo DRY-RUN con delay corto para pruebas
echo ""
echo -e "${GREEN}[INFO] Ejecutando sync (--dry-run)...${NC}"
echo ""
python scripts/sync_publicaciones_to_db.py --delay 1.0 --dry-run

EXIT_CODE=$?

# Desactivar entorno virtual
deactivate

echo ""
echo -e "${GREEN}========================================================================${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}[OK] Test completado exitosamente${NC}"
else
    echo -e "${RED}[ERROR] Test falló con código $EXIT_CODE${NC}"
fi
echo -e "${GREEN}========================================================================${NC}"
echo ""

exit $EXIT_CODE
