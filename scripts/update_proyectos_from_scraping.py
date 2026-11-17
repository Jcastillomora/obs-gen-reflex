"""
update_proyectos_from_scraping.py
----------------------------------
Actualiza proyectos.xlsx haciendo scraping completo desde extranet.ufro.cl

Uso:
    python scripts/update_proyectos_from_scraping.py [--delay FLOAT]

Este script:
1. Lee academicas.xlsx
2. Hace scraping de extranet.ufro.cl para obtener proyectos de cada académica
3. Parsea el campo 'fuente_anios' para extraer fuente, a_inicio, a_fin
4. Guarda/actualiza proyectos.xlsx

Nota: Este script se debe ejecutar ANTES de sync_proyectos_to_db.py
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime
import pandas as pd

# Importar scraper
import sys
sys.path.insert(0, str(Path(__file__).parent))
from scraper_publicaciones import scrape

# =========================================================
# CONFIGURACIÓN
# =========================================================

ROOT = Path(__file__).resolve().parent.parent
ACADEMICAS_FILE = ROOT / "academicas.xlsx"
PROYECTOS_OUTPUT = ROOT / "proyectos.xlsx"


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def parse_fuente_anios(fuente_anios: str) -> tuple:
    """
    Parsea el campo 'fuente_anios' para extraer fuente, a_inicio, a_fin.

    Ejemplos:
    - "FONDECYT 2019-2022" → ("FONDECYT", 2019, 2022)
    - "DIUFRO 2020" → ("DIUFRO", 2020, 2020)
    - "FAPESP BRASIL 2020-2022" → ("FAPESP BRASIL", 2020, 2022)
    """
    if not fuente_anios or pd.isna(fuente_anios):
        return ("", "", "")

    texto = str(fuente_anios).strip()

    # Patrón: "FUENTE YYYY-YYYY" o "FUENTE YYYY"
    # Buscar años al final del string
    match = re.search(r'(\d{4})(?:\s*-\s*(\d{4}))?$', texto)

    if match:
        a_inicio = match.group(1)
        a_fin = match.group(2) if match.group(2) else a_inicio

        # La fuente es todo lo anterior a los años
        fuente = texto[:match.start()].strip()

        return (fuente, a_inicio, a_fin)
    else:
        # No se encontraron años, todo es la fuente
        return (texto, "", "")


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def update_proyectos(delay: float = 1.5):
    """
    Actualiza proyectos.xlsx haciendo scraping completo.

    Args:
        delay: Segundos de espera entre requests (default: 1.5)
    """

    print("=" * 70)
    print("ACTUALIZACION DE PROYECTOS DESDE SCRAPING")
    print("=" * 70)

    # =========================================================
    # 1. CARGAR ACADEMICAS
    # =========================================================

    print(f"\n[1/4] Cargando academicas...")

    if not ACADEMICAS_FILE.exists():
        print(f"ERROR: No se encontro {ACADEMICAS_FILE}")
        return

    df_academicas = pd.read_excel(ACADEMICAS_FILE)
    print(f"   [OK] {len(df_academicas)} academicas encontradas")

    # Preparar DataFrame para scraper (necesita 'nombre', 'apellido1')
    # El archivo tiene 'name' que contiene nombre completo
    # Necesitamos parsearlo o usar una columna existente

    # Verificar si tiene las columnas necesarias
    if 'name' in df_academicas.columns:
        # Parsear nombre completo a nombre y apellidos
        df_scraping = df_academicas.copy()

        # Extraer primer nombre y primer apellido del campo 'name'
        def parse_name(full_name):
            parts = str(full_name).strip().split()
            if len(parts) >= 2:
                nombre = parts[0]
                apellido1 = parts[1]
            elif len(parts) == 1:
                nombre = parts[0]
                apellido1 = ""
            else:
                nombre = ""
                apellido1 = ""
            return pd.Series({'nombre': nombre, 'apellido1': apellido1})

        df_scraping[['nombre', 'apellido1']] = df_scraping['name'].apply(parse_name)
    else:
        print("ERROR: academicas.xlsx debe tener columna 'name'")
        return

    # =========================================================
    # 2. HACER SCRAPING
    # =========================================================

    print(f"\n[2/4] Scrapeando proyectos de {len(df_scraping)} academicas...")
    print(f"   Esto puede tardar varios minutos...")
    print(f"   Delay entre requests: {delay} segundos\n")

    registros = scrape(csv_or_df=df_scraping, delay=delay)

    print(f"\n   [OK] Scraping completado: {len(registros)} registros")

    # =========================================================
    # 3. EXTRAER PROYECTOS
    # =========================================================

    print(f"\n[3/4] Extrayendo proyectos...")

    proyectos_list = []

    for cv in registros:
        rut_ir = cv.rut_ir
        parametro_id = cv.parametro_id
        nombre_completo = cv.nombre_completo

        # Parsear JSON de proyectos
        try:
            proyectos_json = json.loads(cv.proyectos)
        except:
            proyectos_json = []

        for proyecto in proyectos_json:
            fuente_anios = proyecto.get('fuente_anios', '')
            titulo = proyecto.get('titulo', '')
            rol = proyecto.get('rol', '')
            investigadores = proyecto.get('investigadores', '')

            # Parsear fuente_anios para extraer fuente, a_inicio, a_fin
            fuente, a_inicio, a_fin = parse_fuente_anios(fuente_anios)

            proyectos_list.append({
                'rut_ir': rut_ir,
                'parametro_id': parametro_id,
                'nombre_completo': nombre_completo,
                'fuente': fuente,
                'a_inicio': a_inicio,
                'a_fin': a_fin,
                'titulo': titulo,
                'rol': rol,
                'investigadores': investigadores,
            })

    df_proyectos = pd.DataFrame(proyectos_list)

    print(f"   [OK] {len(df_proyectos)} proyectos extraidos")

    # =========================================================
    # 4. GUARDAR PROYECTOS.XLSX
    # =========================================================

    print(f"\n[4/4] Guardando proyectos.xlsx...")

    # Crear backup si existe
    if PROYECTOS_OUTPUT.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        backup_path = PROYECTOS_OUTPUT.parent / f"proyectos_backup_{timestamp}.xlsx"

        import shutil
        shutil.copy2(PROYECTOS_OUTPUT, backup_path)
        print(f"   [OK] Backup creado: {backup_path.name}")

    # Guardar
    df_proyectos.to_excel(PROYECTOS_OUTPUT, index=False)
    print(f"   [OK] proyectos.xlsx actualizado: {len(df_proyectos)} proyectos")

    print(f"\n[OK] Actualizacion completada exitosamente!")
    print(f"\nProximo paso:")
    print(f"  python scripts/sync_proyectos_to_db.py")
    print(f"  (Para sincronizar con proyectos_total.xlsx)")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Actualizar proyectos.xlsx desde scraping")
    parser.add_argument("--delay", type=float, default=1.5, help="Segundos entre requests (default: 1.5)")

    args = parser.parse_args()

    update_proyectos(delay=args.delay)
