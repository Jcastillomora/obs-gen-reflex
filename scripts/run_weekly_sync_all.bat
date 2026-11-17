@echo off
REM Script para ejecutar sincronizacion semanal completa (Windows)
REM Proyectos + Publicaciones
REM
REM Usar en Programador de Tareas:
REM   Desencadenador: Semanal, viernes, 2:00 AM
REM   Programa: C:\ruta\completa\OCDE\scripts\run_weekly_sync_all.bat

echo ======================================================================
echo SINCRONIZACION SEMANAL COMPLETA - OCDE
echo ======================================================================
echo %DATE% %TIME%
echo.

cd /d "%~dp0.."

REM Ejecutar sincronizacion completa
python scripts\run_weekly_sync_all.py --delay 1.5

echo.
echo ======================================================================
echo SINCRONIZACION COMPLETADA
echo ======================================================================
echo %DATE% %TIME%
