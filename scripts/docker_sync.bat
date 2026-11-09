@echo off
REM Script para ejecutar la sincronización de publicaciones dentro del contenedor Docker
REM Uso:
REM   scripts\docker_sync.bat           REM Ejecuta el sync real
REM   scripts\docker_sync.bat --dry-run REM Simula el sync sin modificar archivos

echo ===========================================
echo   Sync de Publicaciones (Docker)
echo ===========================================
echo.
echo Ejecutando sync dentro del contenedor...
echo.

docker compose exec app python scripts/sync_publicaciones_to_db.py %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Sync completado exitosamente
    echo.
    echo Para ver el archivo generado:
    echo   type OCDE\.last_sync.json
    echo.
    echo Los cambios se aplicarán automáticamente.
) else (
    echo.
    echo ✗ Error en el sync
    exit /b %ERRORLEVEL%
)
