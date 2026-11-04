@echo off
REM ============================================================================
REM run_weekly_sync.bat
REM -------------------
REM Script batch para ejecutar el sync semanal de publicaciones en Windows.
REM Diseñado para ser ejecutado por el Programador de tareas de Windows.
REM
REM Configuración del Programador de tareas:
REM 1. Abrir "Programador de tareas" (taskschd.msc)
REM 2. Crear tarea básica
REM 3. Nombre: "OCDE - Sync Semanal Publicaciones"
REM 4. Desencadenador: Semanal, viernes, 2:00 AM
REM 5. Acción: Iniciar un programa
REM    - Programa: C:\Users\Ufro\OneDrive\Escritorio\OCDE\scripts\run_weekly_sync.bat
REM 6. Configurar para ejecutar aunque el usuario no haya iniciado sesión
REM ============================================================================

REM Cambiar al directorio del proyecto
cd /d "C:\Users\Ufro\OneDrive\Escritorio\OCDE"

REM Activar entorno virtual
call env\Scripts\activate.bat

REM Ejecutar sync con delay de 1.5s (respetuoso con el servidor)
python scripts\sync_publicaciones_to_db.py --delay 1.5

REM Guardar código de salida
set EXIT_CODE=%ERRORLEVEL%

REM Desactivar entorno virtual
call env\Scripts\deactivate.bat

REM Salir con el código de salida del script
exit /b %EXIT_CODE%
