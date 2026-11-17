# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**OCDE** (Observatorio de Ciencia y Educación) is a full-stack web app built with the **Reflex** framework (Python). It visualizes research data about women researchers at Universidad de La Frontera (UFRO), tracking projects, publications, and OECD research classifications.

**Producción:** https://observatoriogeneroyciencia.ufro.cl

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize Reflex (first time only, generates .web/ folder and SQLite DB)
reflex init

# Run development server (hot reload, frontend: :3000, backend: :8000)
reflex run

# Apply database migrations
reflex db migrate

# Create a new migration after model changes
reflex db create-migration "description"

# Production build
reflex run --env prod

# Docker deployment
docker-compose up -d
```

The `ANTHROPIC_API_KEY` must be set in `.env` for AI search features to work.

## Setup Inicial y Producción

### Primera instalación o despliegue en nuevo entorno

**IMPORTANTE**: Después de instalar dependencias, SIEMPRE ejecutar las migraciones de base de datos:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. CRÍTICO: Aplicar migraciones de base de datos (crea la tabla 'documento' y otras)
reflex db migrate

# 3. Inicializar Reflex (solo primera vez)
reflex init

# 4. Iniciar la aplicación
reflex run
```

Si omites `reflex db migrate`, la página `/obs_repositorio` mostrará vacía porque la tabla `documento` no existirá, causando el error:
```
sqlite3.OperationalError: no such table: documento
```

### Producción (Docker)

Asegurarse de que el `Dockerfile` o el script de entrada ejecute las migraciones antes de iniciar la aplicación:

```dockerfile
# En Dockerfile o entrypoint.sh
RUN reflex db migrate  # O python -m reflex db migrate
CMD ["reflex", "run", "--env", "prod"]
```

### Despliegue Automático (GitHub Actions)

El proyecto utiliza un **self-hosted runner** de GitHub Actions en el servidor de producción (`srv-obsgenero`) para despliegue automático continuo.

**Workflow:** Cada push a `main` dispara automáticamente:
1. Build de imágenes Docker
2. Reinicio de contenedores
3. Aplicación actualizada en producción (3-5 minutos)

**Monitoreo:**
- Ver workflows: https://github.com/Jcastillomora/obs-gen-reflex/actions
- Ver logs del runner: `sudo journalctl -u actions.runner.* -f`
- Estado del runner: `sudo systemctl status actions.runner.*`

**Despliegue manual** (si el runner no está activo):
```bash
cd ~/obs-gen-reflex
git pull origin main
docker compose build --no-cache
docker compose down && docker compose up -d
```

**Archivos Excel requeridos en producción:**
El `compose.yaml` monta los siguientes archivos Excel desde el host al contenedor:
- `academicas.xlsx` - Lista de investigadoras
- `proyectos_total.xlsx` - Proyectos principal
- `proyectos.xlsx` - Enriquecimiento de proyectos (códigos OCDE, fuente, años)
- `libros_total.xlsx` - Libros publicados
- `publicaciones_total.xlsx` - Publicaciones (actualizado automáticamente por scraper)

**IMPORTANTE:** Si falta alguno de estos archivos en el servidor, `DataCache` mostrará advertencias y los datos estarán incompletos. Verificar con:
```bash
ls -lh *.xlsx
```

## Architecture

### Data Flow

```
Excel files (academicas.xlsx, proyectos_total.xlsx, proyectos.xlsx,
             libros_total.xlsx, publicaciones_total.xlsx)
    → DataCache (singleton, OCDE/backend/data_cache.py)  — loaded once, pre-indexed by RUT
    → State (OCDE/backend/backend.py)                    — Reflex reactive state
    → UI Components (OCDE/views/, OCDE/components/)       — subscribe to state vars
```

Excel files are **not** committed to git (see `.gitignore`). They must be present locally in the `OCDE/` directory or mounted in Docker (see compose.yaml).

### Key Files

| File | Role |
|------|------|
| `OCDE/OCDE.py` | App entry point; defines all pages with `@rx.page` and routes |
| `OCDE/backend/backend.py` | Central Reflex `State` class with all reactive vars and event handlers |
| `OCDE/backend/data_cache.py` | Singleton cache — loads Excel data once and exposes indexed lookups |
| `OCDE/backend/models.py` | SQLAlchemy/Pydantic models: `Investigador`, `Publicaciones`, `Proyectos` |
| `OCDE/backend/data_items.py` | Static config dicts for years, disciplines, and university units (with colors) |
| `OCDE/backend/chatbot/ai_search_agent.py` | Agno + Claude AI agent for natural-language researcher search |
| `OCDE/views/` | Page-level UI components (home, navbar, table, filtros, stats, etc.) |
| `OCDE/components/` | Reusable UI components (chatbot, ai_search, badges, etc.) |
| `rxconfig.py` | Reflex config: app name, TailwindV4Plugin, DB URL |

### Pages & Routes

| Route | Purpose |
|-------|---------|
| `/` | Home with animated cards |
| `/obs_indicadores` | Power BI embed |
| `/obs_otros_indicadores` | Additional indicators |
| `/obs_repositorio` | Repository + chatbot assistant |
| `/obs_contacto` | Contact (Google Forms embed) |
| `/investigadoras` | Researchers list with search/filter |
| `/investigadora/[id]` | Individual researcher profile with projects/publications tabs |

### Reflex Patterns Used

- **`@rx.var`** — computed properties that auto-update when state changes (e.g., `filtered_investigators`)
- **`@rx.event`** — async event handlers triggered by UI interactions
- **`on_load`** — page lifecycle hooks that pre-load data (e.g., `State.load_academicas`)
- **`@rx.mobile_only` / `@rx.desktop_only`** — responsive rendering

### DataCache Details

`DataCache` is a singleton initialized once at startup. It pre-calculates:
- `proyectos_count[rut]` and `publicaciones_count[rut]` for O(1) filter lookups
- `roles_by_rut[rut]` for role filtering
- DataFrames indexed by RUT for fast per-researcher queries

Always use `DataCache` methods rather than reading Excel files directly in state handlers.

### Filtering Pipeline (`filtered_investigators`)

Filters are applied in sequence inside the `@rx.var` computed property:
1. Text search (name, ID, OECD discipline)
2. Area filter (`selected_areas`)
3. Min project count (`min_proyectos`)
4. Min publication count (`min_publicaciones`)
5. Role filter (`search_rol`)

### AI Features

The AI search agent (`ai_search_agent.py`) uses the **Agno** framework with **Anthropic Claude**. It accesses `DataCache` directly (no duplicate file I/O) and returns ranked researcher results with natural-language explanations.

## Tech Stack

- **Reflex** — full-stack reactive Python framework (generates React frontend)
- **Tailwind CSS v4** — via `TailwindV4Plugin` in rxconfig
- **Pandas + openpyxl** — Excel data ingestion
- **SQLAlchemy / SQLModel + Alembic** — ORM and migrations (SQLite locally)
- **Agno + Anthropic** — AI agent for semantic researcher search
- **Docker + Caddy** — production containerization and reverse proxy

## Sincronización Semanal Automatizada

### Overview

El sistema automatiza la actualización completa de **proyectos y publicaciones** mediante scraping de **extranet.ufro.cl** cada viernes a las 2:00 AM.

**Proceso completo:**
1. **Scrapea proyectos.xlsx** desde extranet.ufro.cl
   - Lee `academicas.xlsx` (lista de investigadoras)
   - Extrae proyectos de cada académica
   - Parsea fuente, años, título, rol
   - Actualiza `proyectos.xlsx`
2. **Sincroniza proyectos_total.xlsx**
   - Detecta proyectos nuevos (no existentes en proyectos_total)
   - Mapea `fuente` → `tipo_proyecto`
   - Agrega proyectos con `codigo` y `ocde_2` vacíos
   - Crea backup automático
3. **Sincroniza publicaciones_total.xlsx**
   - Scrapea publicaciones de extranet.ufro.cl
   - Filtra duplicados
   - Agrega solo publicaciones nuevas
   - Crea backup automático
   - Guarda fecha del último scraping en `.last_sync.json`
4. `DataCache` recarga datos al reiniciar la app
5. Página `/investigadoras` muestra fecha de última actualización

### Scripts Disponibles

#### Sincronización Completa (Recomendado)

| Script | Plataforma | Uso |
|--------|------------|-----|
| `scripts/run_weekly_sync_all.py` | Multiplataforma | **Orquestador principal** - ejecuta flujo completo |
| `scripts/test_sync_all.bat` | Windows | Prueba completa (--dry-run) |
| `scripts/test_sync_all.sh` | Linux/Ubuntu | Prueba completa (--dry-run) |
| `scripts/run_weekly_sync_all.bat` | Windows | Ejecución semanal automatizada |
| `scripts/run_weekly_sync_all.sh` | Linux/Ubuntu | Ejecución semanal automatizada |
| `scripts/setup_cron_all.sh` | Ubuntu | Configurar cron job semanal |

#### Scripts Individuales (Uso Manual)

| Script | Plataforma | Uso |
|--------|------------|-----|
| `scripts/update_proyectos_from_scraping.py` | Multiplataforma | Actualizar proyectos.xlsx desde scraping |
| `scripts/sync_proyectos_to_db.py` | Multiplataforma | Sincronizar proyectos_total.xlsx |
| `scripts/sync_publicaciones_to_db.py` | Multiplataforma | Sincronizar publicaciones_total.xlsx |

### Configuración Windows

**Prueba manual (recomendado primero):**
```cmd
# Doble clic en:
scripts\test_sync_all.bat

# O ejecutar directamente:
python scripts\run_weekly_sync_all.py --dry-run
```

**Ejecución manual (modo real):**
```cmd
python scripts\run_weekly_sync_all.py
```

**Automatización semanal (Programador de tareas):**
1. Abrir `taskschd.msc`
2. Crear tarea básica → Nombre: "OCDE - Sync Semanal Completo"
3. Desencadenador: Semanal, viernes, 2:00 AM
4. Acción: Iniciar programa
   - Programa: `C:\Users\Ufro\OneDrive\Escritorio\OCDE\scripts\run_weekly_sync_all.bat`
5. ✓ Ejecutar aunque el usuario no haya iniciado sesión

### Configuración Ubuntu/Linux

**Prueba manual (recomendado primero):**
```bash
bash scripts/test_sync_all.sh

# O ejecutar directamente:
python scripts/run_weekly_sync_all.py --dry-run
```

**Ejecución manual (modo real):**
```bash
python scripts/run_weekly_sync_all.py
```

**Automatización semanal (cron):**
```bash
# Configuración automática:
bash scripts/setup_cron_all.sh

# Configuración manual (crontab -e):
0 2 * * 5 /ruta/completa/OCDE/scripts/run_weekly_sync_all.sh >> /var/log/ocde_sync_all.log 2>&1
```

**Verificar cron:**
```bash
crontab -l                           # Ver crontab actual
tail -f /var/log/ocde_sync_all.log   # Monitorear log en vivo
```

### Configuración Docker (Producción)

**IMPORTANTE**: En producción (Docker), el script debe ejecutarse **dentro del contenedor** usando `docker compose exec`.

**Prerrequisitos:**
1. El archivo `.last_sync.json` debe existir en el host (raíz del proyecto, crearlo vacío si no existe)
2. El `compose.yaml` debe montar correctamente los archivos (ver configuración abajo)

**Configuración de compose.yaml:**
```yaml
volumes:
  # Permitir escritura en archivos Excel
  - ./publicaciones_total.xlsx:/app/publicaciones_total.xlsx
  - ./proyectos_total.xlsx:/app/proyectos_total.xlsx
  - ./proyectos.xlsx:/app/proyectos.xlsx
  # Montar .last_sync.json para persistencia entre reinicios (raíz del proyecto)
  - ./.last_sync.json:/app/.last_sync.json
```

**Prueba manual (desde el servidor de producción):**
```bash
cd ~/obs-gen-reflex

# Prueba completa con --dry-run
docker compose exec app python scripts/run_weekly_sync_all.py --dry-run

# Ejecución real
docker compose exec app python scripts/run_weekly_sync_all.py
```

**Automatización semanal (cron en el host):**
```bash
# Configuración manual (crontab -e):
0 2 * * 5 cd /home/admobge/obs-gen-reflex && docker compose exec -T app python scripts/run_weekly_sync_all.py >> /var/log/ocde_sync_all.log 2>&1
```

**Nota**: El flag `-T` en `docker compose exec -T` es necesario para cron (deshabilita la asignación de pseudo-TTY).

**Verificar cron:**
```bash
crontab -l                           # Ver crontab actual
tail -f /var/log/ocde_sync_all.log   # Monitorear log en vivo
```

**Reinicio del contenedor después del sync:**
NO es necesario reiniciar el contenedor. Los archivos Excel están montados como volúmenes, por lo que los cambios son visibles inmediatamente. Sin embargo, `DataCache` solo recarga al reiniciar la app. Para ver los nuevos datos sin reiniciar, se puede implementar una recarga manual (futuro).

### Parámetros del Script Orquestador

```bash
python scripts/run_weekly_sync_all.py [opciones]

Opciones:
  --delay FLOAT    Segundos entre requests en scraping (default: 1.5)
  --dry-run        Simula sin modificar archivos
```

**Pasos del orquestador:**
1. `update_proyectos_from_scraping.py` - Scrapea y actualiza proyectos.xlsx
2. `sync_proyectos_to_db.py` - Sincroniza proyectos_total.xlsx
3. `sync_publicaciones_to_db.py` - Sincroniza publicaciones_total.xlsx

### Notas Importantes

- **Fuente de datos**: https://extranet.ufro.cl/investigacion se actualiza en tiempo real con nuevos proyectos y publicaciones
- **Scraping semanal**: Todos los viernes a las 2:00 AM se ejecuta automáticamente
- **Detección de duplicados**: Por (RUT normalizado + título normalizado)
- **Backup automático**: Cada ejecución crea backups timestamped:
  - `proyectos_backup_YYYYMMDD_HHMM.xlsx`
  - `proyectos_total_backup_YYYYMMDD_HHMM.xlsx`
  - `publicaciones_total_backup_YYYYMMDD_HHMM.xlsx`
- **Código OCDE pendiente**: Los proyectos nuevos tienen `codigo` y `ocde_2` vacíos. Debes asignarlos manualmente después del sync.
- **Reinicio requerido**: Después del sync, reiniciar `reflex run` para que `DataCache` recargue los datos

### Flujo de Archivos

```
extranet.ufro.cl/investigacion (actualizado en tiempo real)
    ↓ scraping semanal (viernes 2:00 AM)
proyectos.xlsx + publicaciones scrapeadas
    ↓ sincronización automática
proyectos_total.xlsx (con codigo y ocde_2 manuales)
publicaciones_total.xlsx
    ↓ DataCache recarga al reiniciar
Aplicación Web OCDE
```

**Archivos Excel:**
- `academicas.xlsx` - Lista de investigadoras (master list)
- `proyectos.xlsx` - Resultado directo del scraping (auto-generado)
- `proyectos_total.xlsx` - Datos oficiales con códigos OCDE (manual + auto)
- `publicaciones_total.xlsx` - Publicaciones consolidadas (auto)
- `libros_total.xlsx` - Libros publicados (manual)

### Estructura del Scraper

El scraper (`scripts/scraper_publicaciones.py`) extrae de https://extranet.ufro.cl/investigacion:
- **Publicaciones**: tipo (WoS/SciELO/Scopus/Otra), título, revista, autores, año, indexación
- **Proyectos**: fuente, años, título, rol, investigadores

**Parser de Proyectos:**
- `fuente_anios` → `fuente`, `a_inicio`, `a_fin`
  - Ejemplo: "FONDECYT 2019-2022" → fuente="FONDECYT", a_inicio=2019, a_fin=2022
- `fuente` → `tipo_proyecto` (mapeo automático en sync_proyectos_to_db.py)

### Visualización de Fecha de Última Actualización

La página `/investigadoras` muestra automáticamente la fecha del último scraping exitoso.

**Implementación:**
- Al completar un sync exitoso, el script guarda la fecha en `.last_sync.json` (raíz del proyecto):
  ```json
  {
    "last_sync": "2024-11-04T02:00:00",
    "publicaciones_nuevas": 12
  }
  ```
- `State.load_academicas()` carga automáticamente esta fecha al visitar `/investigadoras`
- Se muestra como: **"Última actualización de publicaciones: 04/11/2024 02:00"**
- Si el archivo no existe, el mensaje no se muestra

**Archivos involucrados:**
- `scripts/sync_publicaciones_to_db.py` - función `guardar_fecha_ultimo_sync()`
- `OCDE/backend/backend.py` - función `load_last_sync_date()`
- `OCDE/OCDE.py` - renderizado condicional en `/investigadoras`
- `.last_sync.json` - archivo de metadatos en raíz (gitignored)

**Nota:** El archivo `.last_sync.json` está en `.gitignore` ya que contiene datos dinámicos del sistema.

## Sincronización de Proyectos

### Overview

El sistema permite sincronizar proyectos desde el scraping (`proyectos.xlsx`) a `proyectos_total.xlsx`, agregando solo proyectos nuevos que no existan en el archivo oficial.

**Proceso:**
1. Lee `proyectos.xlsx` (resultado del scraping de extranet.ufro.cl)
2. Lee `proyectos_total.xlsx` (datos oficiales con códigos OCDE)
3. Detecta proyectos que están en el scraping pero NO en proyectos_total
4. Mapea campos automáticamente:
   - `fuente` → `tipo_proyecto` (FONDECYT, DIUFRO, INTERNACIONAL, etc.)
   - `a_inicio` → `año`
   - `titulo`, `rol`, `rut_ir` (normalizado con ceros)
5. Deja `codigo` y `ocde_2` vacíos para asignación manual posterior
6. Crea backup automático antes de guardar

**Scripts Disponibles:**

| Script | Plataforma | Uso |
|--------|------------|-----|
| `scripts/sync_proyectos_to_db.py` | Multiplataforma | Script principal de sincronización |
| `scripts/test_sync_proyectos.bat` | Windows | Prueba manual (--dry-run) |
| `scripts/test_sync_proyectos.sh` | Linux/Ubuntu | Prueba manual (--dry-run) |

### Uso

**Prueba manual (Windows):**
```cmd
# Doble clic en:
scripts\test_sync_proyectos.bat

# O ejecutar directamente con --dry-run:
python scripts\sync_proyectos_to_db.py --dry-run
```

**Prueba manual (Linux/Ubuntu):**
```bash
bash scripts/test_sync_proyectos.sh

# O ejecutar directamente:
python scripts/sync_proyectos_to_db.py --dry-run
```

**Ejecución real (modificar archivos):**
```bash
python scripts/sync_proyectos_to_db.py
```

### Mapeo de Fuentes a Tipos de Proyecto

El script mapea automáticamente el campo `fuente` del scraping al campo `tipo_proyecto`:

| Fuente (scraping) | Tipo Proyecto (proyectos_total) |
|-------------------|----------------------------------|
| "PROYECTOS DE INICIACIÓN, INTERMEDIO Y REGULAR" | FONDECYT |
| "PROYECTOS DIUFRO - FONDOS PROPIOS" | DIUFRO |
| "FONDOS PROPIOS" | FONDOS PROPIOS |
| "FONDEF" | FONDEF |
| "MUJERES EN CIENCIA" | FONDECYT MUJERES |
| "FAPESP BRASIL", "INTERNACIONAL" | INTERNACIONAL |
| Otros | Título capitalizado de la fuente |

### Notas Importantes

- **Código OCDE**: Los proyectos nuevos tienen `codigo` y `ocde_2` vacíos. Debes asignarlos manualmente en `proyectos_total.xlsx` después de la sincronización.
- **Detección de duplicados**: Por (RUT normalizado, título normalizado)
- **Backup automático**: Crea `proyectos_total_backup_YYYYMMDD_HHMM.xlsx` antes de modificar
- **Reinicio requerido**: Después del sync, reiniciar `reflex run` para que `DataCache` recargue los datos
- **Normalización de RUTs**: El script normaliza RUTs con padding de ceros (ej: 97870187 → 097870187)

### Archivos Involucrados

- `proyectos.xlsx` - Resultado del scraping (fuente: `scripts/scraper_publicaciones.py`)
- `proyectos_total.xlsx` - Datos oficiales con códigos OCDE y clasificación
- `scripts/sync_proyectos_to_db.py` - Script de sincronización
- `OCDE/backend/data_cache.py` - Merge de proyectos.xlsx con proyectos_total.xlsx

## Skills disponibles
- @.claude/skills/reflex-dev/SKILL.md — usar para componentes Reflex
- @.claude/skills/agno/SKILL.md — usar para agentes Agno (tools, output_schema, teams, workflows)
