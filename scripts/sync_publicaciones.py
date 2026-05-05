"""
sync_publicaciones.py
---------------------
Ejecuta el scraper y actualiza publicaciones_total.xlsx.
Funciona tanto en desarrollo local como dentro del contenedor Docker.

Uso:
    python scripts/sync_publicaciones.py [--delay 1.5]

Variables de entorno opcionales:
    SCRAPER_DELAY   Segundos entre requests (default: 1.5)
"""

import sys
import os
import json
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime

# ── Rutas (relativas al repositorio, funciona en cualquier OS) ─────────────────
ROOT       = Path(__file__).parent.parent          # raíz del proyecto
SCRIPTS    = Path(__file__).parent                 # scripts/
OUTPUT_FILE = ROOT / "publicaciones_total.xlsx"    # donde lee DataCache

# Archivo de académicas: DataCache lo busca desde la CWD ("./academicas.xlsx")
ACADEMICAS_FILE = ROOT / "academicas.xlsx"

# Delay entre requests
DEFAULT_DELAY = float(os.environ.get("SCRAPER_DELAY", "1.5"))

# ──────────────────────────────────────────────────────────────────────────────

def _generar_csv_investigadores(academicas_path: Path) -> Path:
    """
    Genera un CSV temporal con nombre/apellidos para el scraper,
    a partir de academicas.xlsx (columnas: rut_ir, name).
    Formato de salida: rut_ir, nombre, apellido1, apellido2
    """
    df = pd.read_excel(academicas_path, dtype=str).fillna("")

    def split_nombre(nombre_completo: str) -> dict:
        partes = nombre_completo.strip().split()
        if len(partes) >= 4:
            return {"nombre": " ".join(partes[:-2]), "apellido1": partes[-2], "apellido2": partes[-1]}
        elif len(partes) == 3:
            return {"nombre": partes[0], "apellido1": partes[1], "apellido2": partes[2]}
        elif len(partes) == 2:
            return {"nombre": partes[0], "apellido1": partes[1], "apellido2": ""}
        else:
            return {"nombre": nombre_completo, "apellido1": "", "apellido2": ""}

    df[["nombre", "apellido1", "apellido2"]] = df["name"].apply(
        lambda x: pd.Series(split_nombre(x))
    )

    # Normalizar RUT (igual que DataCache)
    df["rut_ir"] = (
        df["rut_ir"].astype(str).str.strip().str.upper()
        .str.replace(".", "", regex=False).str.lstrip("0")
    )

    csv_path = SCRIPTS / "_investigadores_tmp.csv"
    df[["rut_ir", "nombre", "apellido1", "apellido2"]].to_csv(
        csv_path, index=False, encoding="utf-8-sig"
    )
    print(f"CSV generado: {len(df)} investigadoras → {csv_path.name}")
    return csv_path


def normalizar_rut(serie: pd.Series) -> pd.Series:
    return (
        serie.astype(str).str.strip().str.upper()
        .str.replace(".", "", regex=False).str.lstrip("0")
    )


def main(delay: float = DEFAULT_DELAY):
    inicio = datetime.now()
    print(f"[{inicio:%Y-%m-%d %H:%M}] Iniciando sync de publicaciones...")

    # 0. Verificar académicas
    if not ACADEMICAS_FILE.exists():
        print(f"ERROR: No se encontró {ACADEMICAS_FILE}")
        sys.exit(1)

    # 1. Importar scraper (bundled en scripts/)
    sys.path.insert(0, str(SCRIPTS))
    from scraper_publicaciones import scrape

    # 2. Generar CSV de investigadoras desde academicas.xlsx
    csv_path = _generar_csv_investigadores(ACADEMICAS_FILE)

    try:
        # 3. Ejecutar scraper
        print(f"Scrapeando {csv_path.name} con delay={delay}s ...")
        registros = scrape(str(csv_path), delay=delay)
        print(f"Scraping completado: {len(registros)} CVs procesados")

        # 4. Extraer publicaciones de cada CVInvestigador
        filas = []
        for cv in registros:
            rut = str(getattr(cv, "rut_ir", "")).strip().lstrip("0")
            if not rut:
                continue
            pubs_raw = getattr(cv, "publicaciones", "[]")
            try:
                pubs = json.loads(pubs_raw) if isinstance(pubs_raw, str) else pubs_raw
            except json.JSONDecodeError:
                continue

            for pub in pubs:
                # Extraer año desde el campo revista (formato "..., 2023 ...")
                revista_raw = pub.get("revista", "")
                import re
                m_anio = re.search(r",\s*(\d{4})\s", revista_raw)
                anio = m_anio.group(1) if m_anio else ""

                # Limpiar nombre de revista (antes de "Vol." o primera coma)
                revista_nombre = revista_raw.split(",")[0].split("Vol.")[0].strip()

                filas.append({
                    "año":        anio,
                    "titulo":     pub.get("titulo", ""),
                    "revista":    revista_nombre,
                    "rut_ir":     rut,
                    "indexacion": pub.get("tipo", "Otra"),
                })

        if not filas:
            print("ADVERTENCIA: No se extrajeron publicaciones. Revisa el scraper.")
            sys.exit(1)

        df_nuevo = pd.DataFrame(filas)
        df_nuevo["rut_ir"] = normalizar_rut(df_nuevo["rut_ir"])

        # 5. Backup + guardar nuevo archivo
        if OUTPUT_FILE.exists():
            backup = OUTPUT_FILE.with_name(
                f"publicaciones_total_backup_{inicio:%Y%m%d_%H%M}.xlsx"
            )
            OUTPUT_FILE.rename(backup)
            print(f"Backup: {backup.name}")

        df_nuevo.to_excel(OUTPUT_FILE, index=False)
        fin = datetime.now()
        print(
            f"[{fin:%Y-%m-%d %H:%M}] Sync completada: "
            f"{len(df_nuevo)} publicaciones → {OUTPUT_FILE.name} "
            f"({(fin - inicio).seconds}s)"
        )

    finally:
        # Limpiar CSV temporal
        if csv_path.exists():
            csv_path.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="Segundos entre requests")
    args = parser.parse_args()
    main(delay=args.delay)
