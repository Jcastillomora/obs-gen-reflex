@echo off
REM ============================================================================
REM test_sync_manual.bat
REM --------------------
REM Script de prueba para ejecutar el sync de publicaciones manualmente.
REM NO modifica el Excel (usa --dry-run).
REM
REM Uso:
REM     Doble clic en este archivo o ejecutar desde cmd:
REM     scripts\test_sync_manual.bat
REM ============================================================================

echo.
echo ========================================================================
echo OCDE - Test Sync Semanal de Publicaciones
echo ========================================================================
echo.
echo Este script ejecutara el scraping en modo DRY-RUN (sin modificar Excel)
echo Presiona Ctrl+C para cancelar o cualquier tecla para continuar...
pause > nul

REM Cambiar al directorio del proyecto
cd /d "%~dp0\.."
echo [INFO] Directorio de trabajo: %CD%
echo.

REM Verificar que existe el entorno virtual
if not exist "env\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual en env\
    echo [ERROR] Ejecuta: python -m venv env
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [INFO] Activando entorno virtual...
call env\Scripts\activate.bat

REM Verificar que existe el script
if not exist "scripts\sync_publicaciones_to_db.py" (
    echo [ERROR] No se encontro scripts\sync_publicaciones_to_db.py
    pause
    exit /b 1
)

REM Ejecutar sync en modo DRY-RUN con delay corto para pruebas
echo.
echo [INFO] Ejecutando sync (--dry-run)...
echo.
python scripts\sync_publicaciones_to_db.py --delay 1.0 --dry-run

REM Guardar código de salida
set EXIT_CODE=%ERRORLEVEL%

REM Desactivar entorno virtual
call env\Scripts\deactivate.bat

echo.
echo ========================================================================
if %EXIT_CODE% EQU 0 (
    echo [OK] Test completado exitosamente
) else (
    echo [ERROR] Test fallo con codigo %EXIT_CODE%
)
echo ========================================================================
echo.
echo Presiona cualquier tecla para cerrar...
pause > nul

exit /b %EXIT_CODE%
