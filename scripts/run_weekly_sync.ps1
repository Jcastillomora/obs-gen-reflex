# ============================================================================
# run_weekly_sync.ps1
# -------------------
# Script PowerShell para ejecutar el sync semanal de publicaciones.
# Alternativa al script .bat para usuarios que prefieren PowerShell.
#
# Uso manual:
#     powershell -ExecutionPolicy Bypass -File scripts\run_weekly_sync.ps1
#
# Configuración del Programador de tareas:
# 1. Abrir "Programador de tareas" (taskschd.msc)
# 2. Crear tarea básica
# 3. Nombre: "OCDE - Sync Semanal Publicaciones"
# 4. Desencadenador: Semanal, viernes, 2:00 AM
# 5. Acción: Iniciar un programa
#    - Programa: powershell.exe
#    - Argumentos: -ExecutionPolicy Bypass -File "C:\Users\Ufro\OneDrive\Escritorio\OCDE\scripts\run_weekly_sync.ps1"
# 6. Configurar para ejecutar aunque el usuario no haya iniciado sesión
# ============================================================================

# Configurar encoding para caracteres especiales
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Cambiar al directorio del proyecto
Set-Location "C:\Users\Ufro\OneDrive\Escritorio\OCDE"

# Activar entorno virtual
& "env\Scripts\Activate.ps1"

# Ejecutar sync con delay de 1.5s
python scripts\sync_publicaciones_to_db.py --delay 1.5

# Guardar código de salida
$exitCode = $LASTEXITCODE

# Desactivar entorno virtual
deactivate

# Salir con el código de salida del script
exit $exitCode
