"""
run_weekly_sync_all.py
----------------------
Orquestador de sincronización semanal completa (proyectos + publicaciones)

Este script ejecuta el flujo completo de actualización:
1. Scrapea proyectos.xlsx desde extranet.ufro.cl
2. Sincroniza proyectos nuevos a proyectos_total.xlsx
3. Scrapea y sincroniza publicaciones_total.xlsx

Uso:
    python scripts/run_weekly_sync_all.py [--delay FLOAT] [--dry-run]

Automatización:
    - Windows: Programador de Tareas, viernes 2:00 AM
    - Linux: Cron job, viernes 2:00 AM
"""

import argparse
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# =========================================================
# CONFIGURACIÓN
# =========================================================

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def run_weekly_sync(delay: float = 1.5, dry_run: bool = False):
    """
    Ejecuta sincronización semanal completa.

    Args:
        delay: Segundos entre requests en scraping
        dry_run: Si True, no modifica archivos
    """

    print("=" * 70)
    print("SINCRONIZACION SEMANAL COMPLETA")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Delay: {delay}s")
    print(f"Modo: {'DRY RUN (sin modificar archivos)' if dry_run else 'REAL (modificara archivos)'}")
    print("=" * 70)

    exitosos = 0
    fallidos = 0

    # =========================================================
    # 1. ACTUALIZAR PROYECTOS.XLSX DESDE SCRAPING
    # =========================================================

    print("\n" + "=" * 70)
    print("[PASO 1/3] ACTUALIZAR PROYECTOS.XLSX DESDE SCRAPING")
    print("=" * 70)

    if dry_run:
        print("[INFO] DRY RUN: Saltando scraping de proyectos")
        print("   (En modo real, esto scrapearía extranet.ufro.cl)")
    else:
        script_path = SCRIPTS_DIR / "update_proyectos_from_scraping.py"

        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--delay", str(delay)],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            print(result.stdout)
            print("[OK] Proyectos.xlsx actualizado exitosamente")
            exitosos += 1
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Fallo al actualizar proyectos.xlsx:")
            print(e.stdout)
            print(e.stderr)
            fallidos += 1
            # Continuar con los siguientes pasos aunque falle este

    # =========================================================
    # 2. SINCRONIZAR PROYECTOS_TOTAL.XLSX
    # =========================================================

    print("\n" + "=" * 70)
    print("[PASO 2/3] SINCRONIZAR PROYECTOS A PROYECTOS_TOTAL.XLSX")
    print("=" * 70)

    script_path = SCRIPTS_DIR / "sync_proyectos_to_db.py"
    cmd = [sys.executable, str(script_path)]
    if dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print(result.stdout)
        print("[OK] Proyectos sincronizados exitosamente")
        exitosos += 1
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Fallo al sincronizar proyectos:")
        print(e.stdout)
        print(e.stderr)
        fallidos += 1

    # =========================================================
    # 3. SINCRONIZAR PUBLICACIONES_TOTAL.XLSX
    # =========================================================

    print("\n" + "=" * 70)
    print("[PASO 3/3] SINCRONIZAR PUBLICACIONES A PUBLICACIONES_TOTAL.XLSX")
    print("=" * 70)

    script_path = SCRIPTS_DIR / "sync_publicaciones_to_db.py"
    cmd = [sys.executable, str(script_path), "--delay", str(delay)]
    if dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print(result.stdout)
        print("[OK] Publicaciones sincronizadas exitosamente")
        exitosos += 1
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Fallo al sincronizar publicaciones:")
        print(e.stdout)
        print(e.stderr)
        fallidos += 1

    # =========================================================
    # RESUMEN FINAL
    # =========================================================

    print("\n" + "=" * 70)
    print("RESUMEN DE SINCRONIZACION")
    print("=" * 70)
    print(f"  Exitosos: {exitosos}/3")
    print(f"  Fallidos: {fallidos}/3")

    if fallidos == 0:
        print("\n[OK] Sincronizacion semanal completada exitosamente!")
        if not dry_run:
            print("\n[IMPORTANTE] Reiniciar la aplicacion para que DataCache recargue:")
            print("  reflex run")
    else:
        print(f"\n[WARN] Sincronizacion completada con {fallidos} error(es)")
        print("  Revisar los logs arriba para mas detalles")

    print("=" * 70)

    return fallidos == 0


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sincronizacion semanal completa (proyectos + publicaciones)")
    parser.add_argument("--delay", type=float, default=1.5, help="Segundos entre requests (default: 1.5)")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin modificar archivos")

    args = parser.parse_args()

    success = run_weekly_sync(delay=args.delay, dry_run=args.dry_run)

    # Exit code para cron/scheduler
    sys.exit(0 if success else 1)
