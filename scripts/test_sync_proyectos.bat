@echo off
REM Script para probar sincronizacion de proyectos (Windows)
REM Ejecuta el script en modo DRY RUN (sin modificar archivos)

echo ======================================
echo PRUEBA DE SINCRONIZACION DE PROYECTOS
echo ======================================
echo.
echo Este script ejecuta el sync en modo PRUEBA (--dry-run)
echo NO se modificaran archivos, solo se mostrara que se agregaria
echo.
pause

cd /d "%~dp0.."
python scripts\sync_proyectos_to_db.py --dry-run

echo.
echo ======================================
echo PRUEBA COMPLETADA
echo ======================================
echo.
echo Para ejecutar el sync REAL (modificando archivos):
echo   python scripts\sync_proyectos_to_db.py
echo.
pause
