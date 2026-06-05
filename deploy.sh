#!/bin/bash
set -e

# === Configuración ===
PROJECT_DIR="$HOME/obs-gen-reflex"
BRANCH="main"
COMPOSE_FILE="compose.yaml"
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

# === Git Pull ===
log "Pulling cambios desde GitHub..."
git pull origin "$BRANCH" 2>&1 | tee -a "$LOG_FILE" || fail "Error en git pull"

# === Directorios necesarios ===
mkdir -p assets/uploads

# === Build y Deploy ===
log "Construyendo imágenes y levantando contenedores..."
DOMAIN=observatoriogeneroyciencia.ufro.cl \
    docker compose -f "$COMPOSE_FILE" up -d --build 2>&1 | tee -a "$LOG_FILE"

# === Limpieza ===
log "Limpiando imágenes antiguas..."
docker image prune -f
docker builder prune -f --filter "until=24h"

# === Verificación ===
echo ""
log "Estado de contenedores:"
docker compose -f "$COMPOSE_FILE" ps
echo ""

DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')
log "Uso de disco: $DISK_USAGE"

DISK_PCT=$(echo "$DISK_USAGE" | tr -d '%')
if [ "$DISK_PCT" -gt 80 ]; then
    warn "Disco sobre 80%. Considera limpiar con: docker system prune -a"
fi

echo ""
log "✓ Deploy completado"
log "Log guardado en: $LOG_FILE"
