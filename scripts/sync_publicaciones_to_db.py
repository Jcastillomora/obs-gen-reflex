"""
sync_publicaciones_to_db.py
----------------------------
Script semanal para scraping de publicaciones y actualización de Excel.

Funcionalidad:
1. Lee publicaciones existentes del Excel (evita duplicados)
2. Ejecuta scraper de extranet.ufro.cl
3. Agrega solo publicaciones nuevas al Excel (append)
4. Crea backup automático del Excel anterior
5. Genera reporte de publicaciones agregadas

Uso:
    python scripts/sync_publicaciones_to_db.py [--delay 1.5] [--dry-run]

Opciones:
    --delay     Segundos entre requests (default: 1.5)
    --dry-run   Simula la ejecución sin modificar el Excel

Variables de entorno:
    SCRAPER_DELAY   Override del delay (default: 1.5)

Nota: Las publicaciones se almacenan en Excel, no en base de datos SQLite.
      DataCache las carga en memoria al inicio de la aplicación.
"""

import sys
import os
import json
import argparse
import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple

# Agregar raíz del proyecto al path para imports
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

# Imports del proyecto
from scraper_publicaciones import scrape

# ── Rutas ──────────────────────────────────────────────────────────────────────
ACADEMICAS_FILE = ROOT / "academicas.xlsx"
OUTPUT_EXCEL = ROOT / "publicaciones_total.xlsx"
DB_PATH = ROOT / "data" / "ocde.db"
LAST_SYNC_FILE = ROOT / ".last_sync.json"  # Raíz del proyecto (no OCDE/)

DEFAULT_DELAY = float(os.environ.get("SCRAPER_DELAY", "1.5"))

# ── Helpers ────────────────────────────────────────────────────────────────────
def normalizar_rut(rut: str) -> str:
    """Normaliza RUT (quita puntos, K mayúscula, sin leading zeros)"""
    return str(rut).strip().upper().replace(".", "").lstrip("0")

def extraer_año_revista(revista: str) -> str:
    """Extrae año desde campo revista (formato: ..., 2023 ...)"""
    m = re.search(r",\s*(\d{4})\s", revista)
    return m.group(1) if m else ""

def limpiar_nombre_revista(revista: str) -> str:
    """Limpia nombre de revista (antes de Vol. o primera coma)"""
    return revista.split(",")[0].split("Vol.")[0].strip()

def generar_csv_investigadores(academicas_path: Path) -> Path:
    """Genera CSV temporal con nombre/apellidos para el scraper"""
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
    df["rut_ir"] = df["rut_ir"].apply(normalizar_rut)

    csv_path = Path(__file__).parent / "_investigadores_tmp.csv"
    df[["rut_ir", "nombre", "apellido1", "apellido2"]].to_csv(
        csv_path, index=False, encoding="utf-8-sig"
    )
    return csv_path

def cargar_publicaciones_existentes() -> Set[Tuple[str, str]]:
    """Carga publicaciones existentes del Excel como set de (titulo_lower, rut_ir)"""
    try:
        if not OUTPUT_EXCEL.exists():
            print("      [INFO] No existe Excel previo, todas las publicaciones serán nuevas")
            return set()

        df = pd.read_excel(OUTPUT_EXCEL, dtype=str).fillna("")
        df["rut_ir"] = df["rut_ir"].apply(normalizar_rut)

        return {
            (str(row["titulo"]).lower().strip(), normalizar_rut(row["rut_ir"]))
            for _, row in df.iterrows()
            if row.get("titulo") and row.get("rut_ir")
        }
    except Exception as e:
        print(f"      [WARNING] No se pudo leer Excel existente: {e}")
        return set()

def procesar_scraping_results(registros: list) -> List[Dict]:
    """Convierte resultados del scraper en lista de dicts para publicaciones"""
    filas = []
    for cv in registros:
        rut = normalizar_rut(str(getattr(cv, "rut_ir", "")))
        if not rut:
            continue

        pubs_raw = getattr(cv, "publicaciones", "[]")
        try:
            pubs = json.loads(pubs_raw) if isinstance(pubs_raw, str) else pubs_raw
        except json.JSONDecodeError:
            continue

        for pub in pubs:
            revista_raw = pub.get("revista", "")
            año = extraer_año_revista(revista_raw)
            revista_limpia = limpiar_nombre_revista(revista_raw)

            filas.append({
                "año": año or "Sin info",
                "titulo": pub.get("titulo", "Sin info").strip(),
                "revista": revista_limpia or "Sin info",
                "rut_ir": rut,
                "autor": pub.get("autores", "Sin info").strip(),
                "indexacion": pub.get("tipo", "Otra"),
            })

    return filas

def preparar_dataframe_publicaciones(nuevas: List[Dict]) -> pd.DataFrame:
    """Convierte lista de publicaciones a DataFrame con columnas correctas."""
    df = pd.DataFrame(nuevas)
    # Asegurar orden de columnas consistente con Excel existente
    columnas_ordenadas = ["año", "titulo", "revista", "rut_ir", "autor", "indexacion"]
    return df[columnas_ordenadas]

def guardar_fecha_ultimo_sync(publicaciones_nuevas: int, dry_run: bool = False) -> None:
    """Guarda la fecha del último scraping exitoso en archivo JSON."""
    if dry_run:
        return

    try:
        # Asegurar que el directorio OCDE existe
        LAST_SYNC_FILE.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "last_sync": datetime.now().isoformat(),
            "publicaciones_nuevas": publicaciones_nuevas,
        }

        with open(LAST_SYNC_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"      Fecha de último sync guardada: {data['last_sync']}")
    except Exception as e:
        print(f"      [WARNING] No se pudo guardar fecha de último sync: {e}")

def actualizar_excel(df_nuevas: pd.DataFrame, dry_run: bool = False) -> int:
    """Actualiza Excel con publicaciones nuevas (append). Retorna total final."""
    try:
        if OUTPUT_EXCEL.exists():
            df_existente = pd.read_excel(OUTPUT_EXCEL, dtype=str).fillna("")
            df_combinado = pd.concat([df_existente, df_nuevas], ignore_index=True)
        else:
            df_combinado = df_nuevas

        if dry_run:
            print(f"      [DRY-RUN] Se agregarían {len(df_nuevas)} publicaciones al Excel")
            print(f"      [DRY-RUN] Total final: {len(df_combinado)} publicaciones")
            return len(df_combinado)

        # Backup del anterior
        if OUTPUT_EXCEL.exists():
            backup = OUTPUT_EXCEL.with_name(
                f"publicaciones_total_backup_{datetime.now():%Y%m%d_%H%M}.xlsx"
            )
            OUTPUT_EXCEL.rename(backup)
            print(f"      Backup creado: {backup.name}")

        df_combinado.to_excel(OUTPUT_EXCEL, index=False)
        print(f"      Excel actualizado: {len(df_combinado)} publicaciones totales")
        return len(df_combinado)

    except Exception as e:
        print(f"      [ERROR] No se pudo actualizar Excel: {e}")
        return 0

# ── Main ───────────────────────────────────────────────────────────────────────
def main(delay: float = DEFAULT_DELAY, dry_run: bool = False):
    inicio = datetime.now()
    print("=" * 80)
    print(f"[{inicio:%Y-%m-%d %H:%M}] Sync de publicaciones iniciado")
    print("=" * 80)

    # 1. Verificar archivos
    if not ACADEMICAS_FILE.exists():
        print(f"[ERROR] No se encontró {ACADEMICAS_FILE}")
        sys.exit(1)

    # 2. Cargar publicaciones existentes
    print("\n[1/6] Cargando publicaciones existentes del Excel...")
    existentes = cargar_publicaciones_existentes()
    print(f"      {len(existentes)} publicaciones existentes")

    # 3. Generar CSV de investigadores
    print("\n[2/6] Generando CSV de investigadores...")
    csv_path = generar_csv_investigadores(ACADEMICAS_FILE)
    df_investigadores = pd.read_csv(csv_path)
    print(f"      {len(df_investigadores)} investigadoras")

    try:
        # 4. Ejecutar scraper
        print(f"\n[3/6] Scrapeando extranet.ufro.cl (delay={delay}s)...")
        registros = scrape(str(csv_path), delay=delay)
        print(f"      {len(registros)} CVs procesados")

        # 5. Procesar resultados
        print("\n[4/6] Procesando publicaciones scrapeadas...")
        filas_scrapeadas = procesar_scraping_results(registros)
        print(f"      {len(filas_scrapeadas)} publicaciones scrapeadas")

        # 6. Filtrar duplicados
        print("\n[5/6] Filtrando duplicados...")
        nuevas = []
        for pub in filas_scrapeadas:
            key = (pub["titulo"].lower().strip(), normalizar_rut(pub["rut_ir"]))
            if key not in existentes:
                nuevas.append(pub)

        print(f"      {len(nuevas)} publicaciones NUEVAS")
        print(f"      {len(filas_scrapeadas) - len(nuevas)} duplicados ignorados")

        if len(nuevas) == 0:
            print("\n[OK] No hay publicaciones nuevas para insertar")
            return

        # 7. Actualizar Excel
        print(f"\n[6/6] Actualizando Excel...")
        df_nuevas = preparar_dataframe_publicaciones(nuevas)
        total_final = actualizar_excel(df_nuevas, dry_run=dry_run)

        if not dry_run and total_final > 0:
            print(f"      {len(nuevas)} publicaciones agregadas")
            print(f"      Total en Excel: {total_final}")
            # Guardar fecha del último sync exitoso
            guardar_fecha_ultimo_sync(publicaciones_nuevas=len(nuevas), dry_run=dry_run)

    finally:
        # Limpiar CSV temporal
        if csv_path.exists():
            csv_path.unlink()

    fin = datetime.now()
    print("\n" + "=" * 80)
    print(f"[{fin:%Y-%m-%d %H:%M}] Sync completado en {(fin - inicio).seconds}s")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync semanal de publicaciones")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="Delay entre requests (seg)")
    parser.add_argument("--dry-run", action="store_true", help="Simula sin insertar en DB")
    args = parser.parse_args()

    main(delay=args.delay, dry_run=args.dry_run)
