"""
scraper_publicaciones.py
------------------------
Scraper de publicaciones desde https://extranet.ufro.cl/investigacion

Uso como módulo:
    from scripts.scraper_publicaciones import scrape
    registros = scrape("investigadores.csv", delay=1.5)

Uso standalone:
    python scripts/scraper_publicaciones.py --csv investigadores.csv --delay 1.5

La función scrape() devuelve una lista de CVInvestigador con el campo
'publicaciones' como JSON string.
"""

import re
import json
import time
import argparse
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field, asdict

import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────
BASE        = "https://extranet.ufro.cl/investigacion"
URL_LISTA   = f"{BASE}/cv_investigacion_lst.php"
URL_DETALLE = f"{BASE}/cv_investigador.php"

HEADERS = {
    "User-Agent":       "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0",
    "Content-Type":     "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer":          "https://extranet.ufro.cl/",
    "Origin":           "https://extranet.ufro.cl",
}

# ── Modelos ────────────────────────────────────────────────────────────────────
@dataclass
class Publicacion:
    tipo:    str  # "WoS", "SciELO", "Scopus", "Otra"
    titulo:  str
    revista: str
    autores: str

@dataclass
class Proyecto:
    fuente_anios:  str
    titulo:        str
    rol:           str
    investigadores: str

@dataclass
class CVInvestigador:
    rut_ir:          str = ""
    query_nombre:    str = ""
    query_apellido1: str = ""
    nombre_completo: str = ""
    unidad:          str = ""
    sexo:            str = ""
    parametro_id:    str = ""
    email:           str = ""
    publicaciones:   str = "[]"
    proyectos:       str = "[]"

# ── Helpers ────────────────────────────────────────────────────────────────────
def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def _make_payload(nombre: str, ap1: str, parametro: str = "") -> dict:
    return {
        "Formulario[nombre_filtro]":  nombre,
        "Formulario[paterno_filtro]": ap1,
        "Formulario[materno_filtro]": "",
        "Formulario[cod_sexo]":       "",
        "Formulario[cod_unidad]":     "",
        "Formulario[parametro]":      parametro,
    }

def _detectar_tipo_pub(texto: str) -> str:
    texto_up = texto.upper()
    TIPOS = {"WOS": "WoS", "SCIELO": "SciELO", "SCOPUS": "Scopus", "OTRA": "Otra", "OTRAS": "Otra"}
    for clave, valor in TIPOS.items():
        if clave in texto_up:
            return valor
    return "Otra"

# ── Paso 1: Buscar listado ─────────────────────────────────────────────────────
def _buscar_lista(session: requests.Session, nombre: str, ap1: str) -> list[dict]:
    r = session.post(URL_LISTA, data=_make_payload(nombre, ap1), headers=HEADERS, timeout=15)
    r.encoding = "iso-8859-1"
    soup = BeautifulSoup(r.text, "html.parser")

    resultados = []
    for fila in soup.select("table.Tabla_lst tr"):
        celdas = fila.find_all("td")
        if len(celdas) < 4:
            continue
        link = celdas[1].find("a")
        parametro_id = ""
        if link:
            m = re.search(r"Load\([^,]+,[^,]+,[^,]+,\d+,'([A-Za-z0-9+/=]+)'\)", link.get("href", ""))
            if m:
                parametro_id = m.group(1)
        resultados.append({
            "nombre_completo": _clean(celdas[1].get_text()),
            "unidad":          _clean(celdas[2].get_text()),
            "sexo":            _clean(celdas[3].get_text()),
            "parametro_id":    parametro_id,
        })
    return resultados

# ── Paso 2: Parsear detalle ────────────────────────────────────────────────────
def _parsear_detalle(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Email
    email = ""
    tabla_personal = soup.find("table", class_="Tabla_res")
    if tabla_personal:
        for fila in tabla_personal.find_all("tr"):
            celdas = fila.find_all("td")
            if len(celdas) >= 2:
                label = _clean(celdas[0].get_text()).lower()
                valor = _clean(celdas[-1].get_text())
                if "e-mail" in label:
                    email = valor

    # Publicaciones
    publicaciones   = []
    en_pubs         = False
    tipo_pub_actual = "WoS"

    for tabla in soup.find_all("table", class_=["Tabla_res", "Tabla_res1"]):
        clase    = tabla.get("class", [])
        th       = tabla.find("th")
        es_header = "Tabla_res" in clase and "Tabla_res1" not in clase

        if es_header and th:
            texto = th.get_text().upper()
            if "PUBLICACIONES" in texto:
                en_pubs = True
            elif any(k in texto for k in ("LIBRO", "CAPÍTULO", "PROYECTO", "ACTIVIDAD")):
                en_pubs = False
            continue

        if not en_pubs or "Tabla_res1" not in clase:
            continue

        if th:
            tipo_detectado = _detectar_tipo_pub(th.get_text())
            tipo_pub_actual = tipo_detectado

        tds = tabla.find_all("td")
        if len(tds) >= 3:
            publicaciones.append(asdict(Publicacion(
                tipo    = tipo_pub_actual,
                titulo  = _clean(tds[0].get_text()),
                revista = _clean(tds[1].get_text()),
                autores = _clean(tds[2].get_text()),
            )))

    # Proyectos
    proyectos   = []
    en_proyectos = False

    for tabla in soup.find_all("table", class_=["Tabla_res", "Tabla_res1"]):
        clase    = tabla.get("class", [])
        th       = tabla.find("th")
        es_header = "Tabla_res" in clase and "Tabla_res1" not in clase

        if es_header and th:
            texto = th.get_text().upper()
            if "PROYECTOS" in texto:
                en_proyectos = True
            elif "PUBLICACIONES" in texto or "LIBRO" in texto:
                en_proyectos = False
            continue

        if not en_proyectos or "Tabla_res1" not in clase:
            continue

        tds = tabla.find_all("td")
        if len(tds) >= 1:
            fuente_anios = _clean(th.get_text()) if th else ""
            rol = ""
            if len(tds) > 1:
                span = tds[1].find("span", style=lambda s: s and "FE9900" in s)
                if span:
                    m = re.search(r"\(([^)]+)\)", span.get_text())
                    rol = m.group(1) if m else ""
            proyectos.append(asdict(Proyecto(
                fuente_anios   = fuente_anios,
                titulo         = _clean(tds[0].get_text()),
                rol            = rol,
                investigadores = _clean(tds[1].get_text()) if len(tds) > 1 else "",
            )))

    return {
        "email":        email,
        "publicaciones": json.dumps(publicaciones, ensure_ascii=False),
        "proyectos":    json.dumps(proyectos, ensure_ascii=False),
    }

def _obtener_detalle(session, nombre, ap1, parametro_id) -> dict:
    r = session.post(
        URL_DETALLE,
        data=_make_payload(nombre, ap1, parametro=parametro_id),
        headers=HEADERS,
        timeout=15,
    )
    r.encoding = "iso-8859-1"
    return _parsear_detalle(r.text)

# ── Pipeline principal ─────────────────────────────────────────────────────────
def scrape(ruta_csv: str, delay: float = 1.5) -> list:
    """
    Scrapea publicaciones para cada investigadora en el CSV.

    Args:
        ruta_csv: CSV con columnas rut_ir, nombre, apellido1 (y opcionalmente apellido2)
        delay:    Segundos de espera entre requests

    Returns:
        Lista de CVInvestigador (objetos con .rut_ir y .publicaciones como JSON string)
    """
    df_in = pd.read_csv(ruta_csv, dtype=str).fillna("")
    session = requests.Session()
    session.get(f"{BASE}/ver_cv_investigacion.php", timeout=15)  # obtiene PHPSESSID

    registros = []
    total = len(df_in)

    for i, row in df_in.iterrows():
        nombre = row.get("nombre", "").strip()
        ap1    = row.get("apellido1", "").strip()
        rut    = row.get("rut_ir", "").strip()

        print(f"[{i+1}/{total}] {nombre} {ap1} ...", end=" ", flush=True)

        lista = _buscar_lista(session, nombre, ap1)

        if not lista:
            print("sin resultados")
            registros.append(CVInvestigador(rut_ir=rut, query_nombre=nombre, query_apellido1=ap1))
            time.sleep(delay)
            continue

        print(f"{len(lista)} resultado(s)")

        for item in lista:
            cv = CVInvestigador(
                rut_ir          = rut,
                query_nombre    = nombre,
                query_apellido1 = ap1,
                nombre_completo = item["nombre_completo"],
                unidad          = item["unidad"],
                sexo            = item["sexo"],
                parametro_id    = item["parametro_id"],
            )
            if item["parametro_id"]:
                detalle          = _obtener_detalle(session, nombre, ap1, item["parametro_id"])
                cv.email         = detalle["email"]
                cv.publicaciones = detalle["publicaciones"]
                cv.proyectos     = detalle["proyectos"]
                time.sleep(delay)

            registros.append(cv)

        time.sleep(delay)

    return registros


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper publicaciones UFRO")
    parser.add_argument("--csv",   default="investigadores.csv", help="CSV de entrada")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay entre requests (seg)")
    args = parser.parse_args()

    registros = scrape(args.csv, delay=args.delay)
    print(f"\nTotal CVs scrapeados: {len(registros)}")
