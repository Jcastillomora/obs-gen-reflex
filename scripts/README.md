# Scripts de Sincronización - OCDE

Este directorio contiene los scripts para automatizar la actualización semanal de publicaciones desde extranet.ufro.cl.

## Tabla de Contenidos

- [Overview](#overview)
- [Scripts Disponibles](#scripts-disponibles)
- [Configuración Windows](#configuración-windows)
- [Configuración Ubuntu/Linux](#configuración-ubuntulinux)
- [Uso Manual](#uso-manual)
- [Troubleshooting](#troubleshooting)

---

## Overview

El sistema automatiza la actualización de publicaciones mediante web scraping de **extranet.ufro.cl** cada viernes a las 2:00 AM.

### Flujo del Proceso

```
1. Lee academicas.xlsx (lista de investigadoras)
   ↓
2. Scrapea publicaciones de extranet.ufro.cl
   ↓
3. Filtra duplicados vs publicaciones_total.xlsx existente
   ↓
4. Agrega solo publicaciones NUEVAS al Excel (append)
   ↓
5. Crea backup automático (publicaciones_total_backup_YYYYMMDD_HHMM.xlsx)
   ↓
6. DataCache recarga datos al reiniciar reflex run
```

### ⚠️ Notas Importantes

- **Solo publicaciones**: Los proyectos NO se scrapean automáticamente (requieren código y clasificación OCDE no disponibles en extranet)
- **Detección de duplicados**: Por título (case-insensitive) + RUT investigadora
- **Backup automático**: Se crea en cada ejecución
- **Reinicio requerido**: Después del sync, reiniciar `reflex run` para recargar datos

---

## Scripts Disponibles

### Scripts Principales

| Script | Plataforma | Descripción |
|--------|------------|-------------|
| `sync_publicaciones_to_db.py` | Multiplataforma | Script principal de sincronización |
| `scraper_publicaciones.py` | Multiplataforma | Módulo scraper de extranet.ufro.cl |

### Scripts de Prueba Manual

| Script | Plataforma | Descripción |
|--------|------------|-------------|
| `test_sync_manual.bat` | Windows | Ejecuta sync en modo `--dry-run` (no modifica Excel) |
| `test_sync_manual.sh` | Linux/Ubuntu | Ejecuta sync en modo `--dry-run` (no modifica Excel) |

### Scripts de Automatización

| Script | Plataforma | Descripción |
|--------|------------|-------------|
| `run_weekly_sync.bat` | Windows | Wrapper para Programador de tareas |
| `run_weekly_sync.ps1` | Windows | Wrapper PowerShell (alternativa) |
| `run_weekly_sync.sh` | Linux/Ubuntu | Wrapper para cron |
| `setup_cron_ubuntu.sh` | Ubuntu | Instalador automático de cron job |

### Scripts de Desarrollo

| Script | Plataforma | Descripción |
|--------|------------|-------------|
| `test_sync_quick.py` | Multiplataforma | Prueba rápida con 1 investigadora |
| `test_full_sync.py` | Multiplataforma | Prueba completa del flujo |
| `inspect_extranet_html.py` | Multiplataforma | Inspecciona HTML de extranet |

---

## Configuración Windows

### Opción 1: Programador de Tareas (Recomendado)

1. Presiona `Win + R` y ejecuta: `taskschd.msc`

2. En el panel derecho, click en **"Crear tarea básica..."**

3. **Nombre**: `OCDE - Sync Semanal Publicaciones`
   **Descripción**: `Actualización automática de publicaciones cada viernes`

4. **Desencadenador**: Seleccionar "Semanal"
   - Frecuencia: Cada 1 semana
   - Día: Viernes
   - Hora: 2:00 AM

5. **Acción**: Seleccionar "Iniciar un programa"
   - Programa: `C:\Users\Ufro\OneDrive\Escritorio\OCDE\scripts\run_weekly_sync.bat`

6. **Configuración avanzada** (en Propiedades de la tarea):
   - ✅ Ejecutar tanto si el usuario inició sesión como si no
   - ✅ Ejecutar con los privilegios más altos
   - ✅ Si la tarea ya se está ejecutando, No iniciar una nueva instancia

7. Click en **Finalizar**

### Opción 2: PowerShell (Alternativa)

Si prefieres usar PowerShell:

```powershell
# Editar la ruta en run_weekly_sync.ps1 si es necesario
powershell -ExecutionPolicy Bypass -File scripts\run_weekly_sync.ps1
```

Luego configurar en Programador de tareas con:
- Programa: `powershell.exe`
- Argumentos: `-ExecutionPolicy Bypass -File "C:\Users\Ufro\OneDrive\Escritorio\OCDE\scripts\run_weekly_sync.ps1"`

### Prueba Manual (Windows)

Doble click en:
```
scripts\test_sync_manual.bat
```

O desde cmd:
```cmd
cd C:\Users\Ufro\OneDrive\Escritorio\OCDE
scripts\test_sync_manual.bat
```

---

## Configuración Ubuntu/Linux

### Opción 1: Setup Automático (Recomendado)

```bash
cd /ruta/a/OCDE
bash scripts/setup_cron_ubuntu.sh
```

Este script:
- Hace ejecutables los scripts necesarios
- Crea el archivo de log en `/var/log/ocde_sync.log`
- Agrega la entrada al crontab
- Configura ejecución cada viernes a las 2:00 AM

### Opción 2: Configuración Manual

1. Hacer ejecutable el script:
   ```bash
   chmod +x scripts/run_weekly_sync.sh
   ```

2. Editar crontab:
   ```bash
   crontab -e
   ```

3. Agregar la siguiente línea (reemplazar `/ruta/a/OCDE` con la ruta real):
   ```cron
   0 2 * * 5 /ruta/a/OCDE/scripts/run_weekly_sync.sh >> /var/log/ocde_sync.log 2>&1
   ```

4. Guardar y salir (en vim: `:wq`, en nano: `Ctrl+O`, `Enter`, `Ctrl+X`)

### Comandos Útiles (Linux)

```bash
# Ver tareas cron configuradas
crontab -l

# Editar tareas cron
crontab -e

# Eliminar todas las tareas cron (¡CUIDADO!)
crontab -r

# Ver log en tiempo real
tail -f /var/log/ocde_sync.log

# Ver últimas 50 líneas del log
tail -n 50 /var/log/ocde_sync.log

# Probar el script manualmente
bash scripts/run_weekly_sync.sh
```

### Prueba Manual (Ubuntu/Linux)

```bash
cd /ruta/a/OCDE
bash scripts/test_sync_manual.sh
```

---

## Uso Manual

### Ejecutar Sync Completo (modifica Excel)

**Windows:**
```cmd
cd C:\Users\Ufro\OneDrive\Escritorio\OCDE
env\Scripts\activate
python scripts\sync_publicaciones_to_db.py
```

**Linux:**
```bash
cd /ruta/a/OCDE
source env/bin/activate
python scripts/sync_publicaciones_to_db.py
```

### Ejecutar en Modo Dry-Run (solo prueba)

**Windows:**
```cmd
python scripts\sync_publicaciones_to_db.py --dry-run
```

**Linux:**
```bash
python scripts/sync_publicaciones_to_db.py --dry-run
```

### Parámetros Disponibles

```bash
python scripts/sync_publicaciones_to_db.py [opciones]

Opciones:
  --delay FLOAT    Segundos entre requests HTTP (default: 1.5)
  --dry-run        Simula ejecución sin modificar Excel
```

**Ejemplos:**

```bash
# Delay más rápido (solo para pruebas)
python scripts/sync_publicaciones_to_db.py --delay 0.5

# Delay más lento (más respetuoso con el servidor)
python scripts/sync_publicaciones_to_db.py --delay 3.0

# Dry-run con delay personalizado
python scripts/sync_publicaciones_to_db.py --delay 1.0 --dry-run
```

---

## Troubleshooting

### Error: "No se encontró el entorno virtual"

**Solución:**
```bash
# Crear entorno virtual
python -m venv env  # Windows
python3 -m venv env # Linux

# Activar e instalar dependencias
source env/bin/activate  # Linux
env\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Error: "No se encontró academicas.xlsx"

**Causa:** El archivo `academicas.xlsx` no existe en la raíz del proyecto.

**Solución:** Verificar que el archivo existe:
```bash
ls academicas.xlsx  # Linux
dir academicas.xlsx # Windows
```

### Error: HTTP timeout o connection refused

**Causa:** Problemas de conectividad con extranet.ufro.cl

**Solución:**
1. Verificar conexión a internet
2. Verificar que extranet.ufro.cl está accesible
3. Aumentar el delay: `--delay 3.0`

### Cron no ejecuta el script (Linux)

**Verificación:**
```bash
# Ver log del sistema
sudo grep CRON /var/log/syslog

# Verificar que el script es ejecutable
ls -l scripts/run_weekly_sync.sh

# Debe mostrar: -rwxr-xr-x (permiso de ejecución)
```

**Solución:**
```bash
chmod +x scripts/run_weekly_sync.sh
```

### Excel no se actualiza después del sync

**Causa:** DataCache no ha recargado los datos.

**Solución:**
1. Verificar que el sync completó exitosamente (revisar log)
2. Reiniciar la aplicación Reflex:
   ```bash
   # Ctrl+C para detener
   reflex run
   ```

### Publicaciones duplicadas en el Excel

**Causa:** El filtro de duplicados falló (títulos muy similares pero no idénticos).

**Solución manual:**
1. Abrir `publicaciones_total.xlsx`
2. Usar filtros de Excel para encontrar duplicados
3. Eliminar manualmente
4. Guardar

**Prevención:** El script detecta duplicados por título exacto (case-insensitive) + RUT.

---

## Estructura del Scraper

El scraper (`scraper_publicaciones.py`) extrae información de https://extranet.ufro.cl/investigacion:

### Datos Extraídos

**Publicaciones:**
- Tipo de indexación (WoS, SciELO, Scopus, Otra)
- Título
- Revista
- Autores
- Año (extraído del campo revista)

**Proyectos (parseados pero NO guardados):**
- Fuente y rango de años (ej: "FONDECYT 2020-2023")
- Título
- Rol (Investigador Responsable, Co-Investigador)
- Investigadores participantes

### ¿Por qué no se guardan los proyectos?

Los proyectos en extranet **NO incluyen**:
- Código del proyecto (CIV23-0001, DFP18-0005, etc.)
- Clasificación OCDE (necesaria para filtros)

Estos campos son esenciales para el funcionamiento del observatorio y deben gestionarse manualmente.

---

## Logs y Monitoreo

### Ubicación de Logs

**Windows:**
- Salida en consola (si se ejecuta manualmente)
- No hay log persistente por defecto

**Linux:**
- `/var/log/ocde_sync.log` (configurado en cron)

### Formato de Log

```
[2024-11-02 02:00:15] ==========================================================================
[2024-11-02 02:00:15] OCDE - Sync Semanal de Publicaciones
[2024-11-02 02:00:15] ==========================================================================
[2024-11-02 02:00:15] Directorio de trabajo: /home/user/OCDE
[2024-11-02 02:00:15] Activando entorno virtual...
[2024-11-02 02:00:16] Ejecutando sync de publicaciones...
...
[2024-11-02 02:05:42] ==========================================================================
[2024-11-02 02:05:42] [OK] Sync completado exitosamente
[2024-11-02 02:05:42] ==========================================================================
```

---

## Contribución

Al modificar estos scripts, seguir estas convenciones:

1. **Mantener compatibilidad Windows/Linux**
2. **Usar rutas relativas** (no hardcodear rutas absolutas)
3. **Agregar logging descriptivo**
4. **Documentar cambios** en este README
5. **Probar con `--dry-run`** antes de commit

---

## Referencias

- Script principal: `sync_publicaciones_to_db.py`
- Scraper: `scraper_publicaciones.py`
- Documentación principal: `../CLAUDE.md`
- Fuente de datos: https://extranet.ufro.cl/investigacion
