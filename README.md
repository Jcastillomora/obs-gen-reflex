# Observatorio de Género y Ciencia — UFRO

Plataforma web para visualizar y explorar datos de investigadoras de la Universidad de La Frontera (UFRO). Permite consultar proyectos, publicaciones y clasificaciones disciplinarias OCDE con búsqueda inteligente por lenguaje natural.

---

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Framework web | [Reflex](https://reflex.dev) 0.8.6 — Python full-stack, compila a React |
| Estilos | Tailwind CSS v4 vía `TailwindV4Plugin` |
| Base de datos | SQLite + SQLAlchemy / SQLModel + Alembic |
| Datos Excel | Pandas + openpyxl |
| IA | [Agno](https://docs.agno.com) + Claude (Anthropic) |
| Autenticación | [reflex-clerk](https://kroo.github.io/reflex-clerk/) |
| Contenedores | Docker + Docker Compose |
| Reverse proxy | Caddy (HTTPS automático) |
| CI/CD | GitHub Actions + self-hosted runner |

---

## Estructura del proyecto

```
OCDE/
├── OCDE/
│   ├── OCDE.py                    # Punto de entrada — define todas las páginas y rutas
│   ├── backend/
│   │   ├── backend.py             # Estado central Reflex (State) y event handlers
│   │   ├── data_cache.py          # Singleton: carga Excel una vez, expone índices O(1)
│   │   ├── models.py              # Modelos SQLAlchemy: Investigador, Publicaciones, Proyectos
│   │   ├── data_items.py          # Configuración estática: años, disciplinas, unidades
│   │   ├── admin_state.py         # CRUD de documentos para panel admin
│   │   └── chatbot/
│   │       ├── ai_search_agent.py # Agente Agno para búsqueda semántica
│   │       └── pdf_agent.py       # Agente para consultas sobre documentos PDF
│   ├── views/                     # Componentes de página (home, tabla, filtros, stats…)
│   └── components/                # Componentes reutilizables (chatbot, badges, AI search…)
├── assets/
│   └── uploads/                   # PDFs subidos desde el panel admin (persistidos en volumen)
├── compose.yaml                   # Orquestación Docker (app + Caddy)
├── Dockerfile                     # Build multi-stage: Python 3.13 → slim
├── Caddyfile                      # Configuración del reverse proxy
├── deploy.sh                      # Script de deploy en el servidor
├── rxconfig.py                    # Configuración Reflex (app name, plugins, DB URL)
└── requirements.txt
```

---

## Páginas y rutas

| Ruta | Descripción |
|------|-------------|
| `/` | Inicio con tarjetas animadas y noticias |
| `/investigadoras` | Listado de investigadoras con búsqueda y filtros |
| `/investigadora/[id]` | Perfil individual con tabs de proyectos y publicaciones |
| `/obs_indicadores` | Embed Power BI |
| `/obs_otros_indicadores` | Indicadores adicionales |
| `/obs_repositorio` | Repositorio de documentos + chatbot asistente |
| `/obs_contacto` | Formulario de contacto (Google Forms embed) |
| `/admin` | Panel administrativo (protegido con Clerk) |

---

## Agentes de IA

### Agente de búsqueda (`ai_search_agent.py`)

Permite buscar investigadoras en lenguaje natural. Usa el framework **Agno** con el modelo `claude-haiku-4-5` de Anthropic.

**Herramientas disponibles:**

| Tool | Descripción |
|------|-------------|
| `listar_areas_ocde` | Lista todas las áreas OCDE disponibles |
| `buscar_investigadoras_por_nombre` | Búsqueda por nombre o apellido |
| `buscar_investigadoras_por_area` | Filtro por área OCDE |
| `buscar_publicacion_por_titulo` | Localiza publicaciones por fragmento de título |
| `buscar_proyecto_por_titulo` | Localiza proyectos por fragmento de título |
| `buscar_por_termino_libre` | Búsqueda semántica amplia con ranking de relevancia |
| `obtener_estadisticas` | Totales generales del repositorio |

El agente retorna un objeto `SearchResult` (Pydantic) con campos estructurados: `tipo_busqueda`, `areas_detectadas`, `nombres_detectados`, `min_proyectos`, `min_publicaciones`, `rol_filtro` y `resumen`. Si la API no está disponible, cae en un modo de búsqueda simple por regex.

### Agente de documentos (`pdf_agent.py`)

Responde preguntas sobre los PDFs del repositorio usando los documentos subidos desde el panel admin.

---

## Instalación local

### Requisitos

- Python 3.12+
- Node.js 18+ (Reflex lo gestiona automáticamente)
- Archivos Excel en `OCDE/`: `academicas.xlsx`, `proyectos_total.xlsx`, `publicaciones_total.xlsx`

### Pasos

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd obs-gen-reflex

# 2. Crear y activar entorno virtual
python -m venv env
source env/bin/activate      # Linux/macOS
env\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con los valores correspondientes

# 5. Inicializar Reflex (primera vez)
reflex init

# 6. Aplicar migraciones de base de datos
reflex db migrate

# 7. Iniciar servidor de desarrollo
reflex run
```

La app queda disponible en `http://localhost:3000`.

### Variables de entorno (`.env`)

```env
ANTHROPIC_API_KEY=sk-ant-...          # Requerida para búsqueda IA
CLERK_PUBLISHABLE_KEY=pk_test_...     # Autenticación frontend
CLERK_SECRET_KEY=sk_test_...          # Autenticación backend
```

---

## Deploy con Docker

```bash
# Construir y levantar
DOMAIN=tu-dominio.cl docker compose up -d --build

# Ver logs
docker compose logs -f app

# Aplicar migraciones en producción
docker compose exec app reflex db migrate
```

---

## CI/CD

El deploy automático se activa con cada push a `main`:

```
Push a main
  → GitHub Actions
  → Self-hosted runner (servidor)
  → git pull origin main
  → bash deploy.sh
      → docker compose up -d --build --force-recreate
      → limpieza de imágenes Docker
      → alerta automática si disco > 80%
```

El runner se ejecuta directamente en el servidor, sin necesidad de abrir puertos SSH externos.

---

## Comandos útiles

```bash
reflex run                          # Servidor de desarrollo
reflex db migrate                   # Aplicar migraciones
reflex db create-migration "desc"   # Nueva migración tras cambios en modelos
docker compose logs -f app          # Logs del backend en producción
docker system prune -a              # Limpieza profunda de Docker
```
