#!/bin/bash
set -e

# === Configuración ===
BRANCH="main"
COMPOSE_FILE="compose.yaml"

# Cargar variables del servidor (no están en git)
DEPLOY_ENV="$(dirname "$0")/.env.deploy"
if [ -f "$DEPLOY_ENV" ]; then
    source "$DEPLOY_ENV"
else
    echo "ERROR: Falta .env.deploy en el directorio del proyecto" >&2
    exit 1
fi

LOG_FILE="$PROJECT_DIR/deploy.log"

# === Colores ===
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠ $1${NC}"; }
fail() { echo -e "${RED}[$(date '+%H:%M:%S')] ✗ $1${NC}"; exit 1; }

echo ""
log "========================================="
log "  Deploy Observatorio de Género y Ciencia"
log "========================================="
echo ""

cd "$PROJECT_DIR" || fail "No se encontró $PROJECT_DIR"

# Verificar rama
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    fail "Rama incorrecta: '$CURRENT_BRANCH'. Se esperaba '$BRANCH'"
fi

# === Directorios necesarios ===
mkdir -p assets/uploads

# === Build y Deploy ===
log "Construyendo imagen de la app..."
DOMAIN="$DOMAIN" \
    docker compose -f "$COMPOSE_FILE" build app 2>&1 | tee -a "$LOG_FILE"

log "Construyendo imagen del webserver (sin caché)..."
DOMAIN="$DOMAIN" \
    docker compose -f "$COMPOSE_FILE" build --no-cache webserver 2>&1 | tee -a "$LOG_FILE"

log "Levantando contenedores..."
DOMAIN="$DOMAIN" \
    docker compose -f "$COMPOSE_FILE" up -d --force-recreate 2>&1 | tee -a "$LOG_FILE"

# === Limpieza ===
log "Limpiando imágenes y cache Docker..."
docker image prune -f
docker builder prune -f

# === Verificación ===
echo ""
log "Estado de contenedores:"
docker compose -f "$COMPOSE_FILE" ps
echo ""

DISK_PCT=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}')
log "Uso de disco: ${DISK_PCT}%"

if [ "$DISK_PCT" -gt 80 ]; then
    warn "Disco sobre 80% — ejecutando limpieza profunda..."
    docker system prune -f
    DISK_PCT=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}')
    log "Uso de disco tras limpieza: ${DISK_PCT}%"
fi

echo ""
log "✓ Deploy completado"
log "Log guardado en: $LOG_FILE"
