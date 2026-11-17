"""
sync_proyectos_to_db.py
-----------------------
Sincroniza proyectos desde proyectos.xlsx (scraping) a proyectos_total.xlsx

Uso:
    python scripts/sync_proyectos_to_db.py [--dry-run]

Lógica:
1. Lee proyectos.xlsx (resultado del scraping de extranet.ufro.cl)
2. Lee proyectos_total.xlsx (datos oficiales con códigos OCDE)
3. Detecta proyectos que están en el scraping pero NO en proyectos_total
4. Los agrega a proyectos_total.xlsx con:
   - fuente → tipo_proyecto
   - a_inicio → año
   - titulo, rol, rut_ir (normalizado)
   - codigo = "" (para asignar manualmente después)
   - ocde_2 = "" (para asignar manualmente después)
5. Crea backup automático antes de guardar
"""

import argparse
import unicodedata
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# =========================================================
# CONFIGURACIÓN
# =========================================================

# Rutas de archivos
ROOT = Path(__file__).resolve().parent.parent
PROYECTOS_SCRAPING_FILE = ROOT / "proyectos.xlsx"  # Resultado del scraping
PROYECTOS_TOTAL_FILE = ROOT / "proyectos_total.xlsx"  # Datos oficiales


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparación (sin tildes, minúsculas, sin espacios extra)."""
    if pd.isna(texto) or texto == "":
        return ""
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"\s+", " ", texto)
    return texto


def normalizar_rut(rut: str) -> str:
    """Normaliza RUT: quita puntos, guiones, uppercase, padding con ceros."""
    if pd.isna(rut) or rut == "":
        return ""

    rut_str = str(rut).strip().upper().replace(".", "").replace("-", "")

    # Si termina en dígito verificador (letra), separarlo
    if rut_str[-1].isalpha():
        numero = rut_str[:-1]
        dv = rut_str[-1]
        # Padding con ceros a 8 dígitos + DV
        return numero.zfill(8) + dv
    else:
        # Solo números, padding a 9 dígitos
        return rut_str.zfill(9)


def mapear_fuente_a_tipo(fuente: str) -> str:
    """
    Mapea el campo 'fuente' de proyectos.xlsx al campo 'tipo_proyecto'.

    Ejemplos:
    - "FAPESP BRASIL" → "INTERNACIONAL"
    - "PROYECTOS DE INICIACIÓN, INTERMEDIO Y REGULAR" → "FONDECYT"
    - "PROYECTOS DIUFRO - FONDOS PROPIOS" → "DIUFRO"
    """
    fuente_lower = fuente.lower()

    # Mapeo de patrones conocidos
    if "fondecyt" in fuente_lower or "iniciación" in fuente_lower or "intermedio" in fuente_lower or "regular" in fuente_lower:
        return "FONDECYT"
    elif "diufro" in fuente_lower:
        return "DIUFRO"
    elif "fondos propios" in fuente_lower:
        return "FONDOS PROPIOS"
    elif "fondef" in fuente_lower:
        return "FONDEF"
    elif "mujeres en ciencia" in fuente_lower:
        return "FONDECYT MUJERES"
    elif "internacional" in fuente_lower or "brasil" in fuente_lower or "europa" in fuente_lower:
        return "INTERNACIONAL"
    elif "privado" in fuente_lower or "empresa" in fuente_lower:
        return "PRIVADO"
    else:
        # Si no matchea ningún patrón, usar la fuente original (título capitalizado)
        return fuente.strip().title()


def crear_backup(file_path: Path) -> Path:
    """Crea un backup del archivo con timestamp."""
    if not file_path.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"

    import shutil
    shutil.copy2(file_path, backup_path)

    return backup_path


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def sync_proyectos(dry_run: bool = False):
    """
    Sincroniza proyectos desde proyectos.xlsx a proyectos_total.xlsx.

    Args:
        dry_run: Si True, solo muestra qué se agregaría sin modificar archivos
    """

    print("=" * 70)
    print("SINCRONIZACIÓN DE PROYECTOS")
    print("=" * 70)

    # =========================================================
    # 1. CARGAR ARCHIVOS
    # =========================================================

    print(f"\n[1/5] Cargando archivos...")

    if not PROYECTOS_SCRAPING_FILE.exists():
        print(f"ERROR: No se encontro {PROYECTOS_SCRAPING_FILE}")
        return

    if not PROYECTOS_TOTAL_FILE.exists():
        print(f"ERROR: No se encontro {PROYECTOS_TOTAL_FILE}")
        return

    df_scraping = pd.read_excel(PROYECTOS_SCRAPING_FILE)
    df_total = pd.read_excel(PROYECTOS_TOTAL_FILE)

    print(f"   [OK] proyectos.xlsx (scraping): {len(df_scraping)} proyectos")
    print(f"   [OK] proyectos_total.xlsx: {len(df_total)} proyectos")

    # =========================================================
    # 2. NORMALIZAR DATOS
    # =========================================================

    print(f"\n[2/5] Normalizando datos...")

    # Normalizar RUTs
    df_scraping["rut_norm"] = df_scraping["rut_ir"].apply(normalizar_rut)
    df_total["rut_norm"] = df_total["rut_ir"].apply(normalizar_rut)

    # Normalizar títulos
    df_scraping["titulo_norm"] = df_scraping["titulo"].apply(normalizar_texto)
    df_total["titulo_norm"] = df_total["titulo"].apply(normalizar_texto)

    print(f"   [OK] RUTs y títulos normalizados")

    # =========================================================
    # 3. DETECTAR DUPLICADOS
    # =========================================================

    print(f"\n[3/5] Detectando proyectos nuevos...")

    # Crear índice de proyectos existentes en proyectos_total
    # Formato: (rut_norm, titulo_norm) → True
    existentes = set()
    for _, row in df_total.iterrows():
        rut_norm = row["rut_norm"]
        titulo_norm = row["titulo_norm"]
        if rut_norm and titulo_norm:
            existentes.add((rut_norm, titulo_norm))

    print(f"   [OK] Proyectos existentes indexados: {len(existentes)}")

    # Filtrar proyectos nuevos (que están en scraping pero NO en total)
    nuevos = []
    for _, row in df_scraping.iterrows():
        rut_norm = row["rut_norm"]
        titulo_norm = row["titulo_norm"]

        if not rut_norm or not titulo_norm:
            continue

        if (rut_norm, titulo_norm) not in existentes:
            nuevos.append(row)

    print(f"   [OK] Proyectos nuevos detectados: {len(nuevos)}")

    if len(nuevos) == 0:
        print(f"\n[OK] No hay proyectos nuevos para agregar. Todo sincronizado!")
        return

    # =========================================================
    # 4. PREPARAR NUEVOS PROYECTOS
    # =========================================================

    print(f"\n[4/5] Preparando {len(nuevos)} proyectos nuevos...")

    registros_nuevos = []

    for row in nuevos:
        # Mapear campos de scraping a formato de proyectos_total
        # Formato esperado en proyectos_total.xlsx:
        # ['codigo', 'titulo', 'año', 'ocde_2', 'tipo_proyecto', 'investigador_responsable', 'rut_ir', 'rol']

        rut_ir = row["rut_norm"]  # RUT normalizado con ceros
        titulo = row["titulo"]
        rol = row.get("rol", "")
        fuente = row.get("fuente", "")
        a_inicio = row.get("a_inicio", "")

        # Convertir a_inicio a año (int)
        if pd.notna(a_inicio):
            try:
                año = int(float(a_inicio))
            except:
                año = 0
        else:
            año = 0

        # Mapear fuente → tipo_proyecto
        tipo_proyecto = mapear_fuente_a_tipo(fuente) if fuente else ""

        nuevo_registro = {
            "codigo": "",  # Vacío para asignar manualmente
            "titulo": titulo,
            "año": año,
            "ocde_2": "",  # Vacío para asignar manualmente
            "tipo_proyecto": tipo_proyecto,
            "investigador_responsable": "",  # No disponible en scraping
            "rut_ir": rut_ir,
            "rol": rol,
        }

        registros_nuevos.append(nuevo_registro)

    df_nuevos = pd.DataFrame(registros_nuevos)

    print(f"   [OK] {len(df_nuevos)} registros preparados")

    # Mostrar muestra de proyectos nuevos
    print(f"\n Muestra de proyectos a agregar (primeros 5):")
    for i, row in df_nuevos.head(5).iterrows():
        print(f"\n   {i+1}. {row['titulo'][:70]}")
        print(f"      RUT: {row['rut_ir']}")
        print(f"      Año: {row['año']}")
        print(f"      Tipo: {row['tipo_proyecto']}")
        print(f"      Rol: {row['rol']}")

    if len(df_nuevos) > 5:
        print(f"\n   ... y {len(df_nuevos) - 5} proyectos más")

    # =========================================================
    # 5. GUARDAR CAMBIOS
    # =========================================================

    if dry_run:
        print(f"\n[3/5] DRY RUN: No se guardaron cambios (usar sin --dry-run para guardar)")
        return

    print(f"\n[5/5] Guardando cambios...")

    # Crear backup
    backup_path = crear_backup(PROYECTOS_TOTAL_FILE)
    if backup_path:
        print(f"   [OK] Backup creado: {backup_path.name}")

    # Concatenar proyectos existentes + nuevos
    df_total_updated = pd.concat([df_total.drop(columns=["rut_norm", "titulo_norm"]), df_nuevos], ignore_index=True)

    # Guardar
    df_total_updated.to_excel(PROYECTOS_TOTAL_FILE, index=False)
    print(f"   [OK] proyectos_total.xlsx actualizado: {len(df_total)} -> {len(df_total_updated)} proyectos")

    print(f"\n[OK] Sincronizacion completada exitosamente!")
    print(f"    Proyectos agregados: {len(df_nuevos)}")
    print(f"\n[WARN]  IMPORTANTE: Los proyectos nuevos tienen 'codigo' y 'ocde_2' vacios.")
    print(f"   Debes asignarlos manualmente en proyectos_total.xlsx")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sincronizar proyectos desde scraping a proyectos_total.xlsx")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin guardar cambios")

    args = parser.parse_args()

    sync_proyectos(dry_run=args.dry_run)
