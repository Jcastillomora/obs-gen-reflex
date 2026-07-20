# data_cache.py - Caché de datos compartido
"""
Módulo singleton para caché de datos.
Usado por backend.py y ai_search_agent.py para evitar cargar Excel múltiples veces.

UBICACIÓN: OCDE/backend/data_cache.py
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Set
import logging
import os

logger = logging.getLogger(__name__)


# =========================================================
# CONFIGURACIÓN DE ARCHIVOS
# =========================================================
PROYECTOS_FILE = "proyectos_total.xlsx"
PROYECTOS_EXTRA_FILE = "proyectos.xlsx"
ACADEMICAS_FILE = "academicas.xlsx"
PUBLICACIONES_FILE = "publicaciones_total.xlsx"
LIBROS_FILE = "libros_total.xlsx"


class DataCache:
    """
    Singleton para caché de datos compartido.
    Se inicializa UNA sola vez y es usado por todo el sistema.
    """
    _instance: Optional['DataCache'] = None
    _initialized: bool = False
    _data_directory: str = "./"
    
    # DataFrames cargados
    df_academicas: Optional[pd.DataFrame] = None
    df_proyectos: Optional[pd.DataFrame] = None
    df_proyectos_extra: Optional[pd.DataFrame] = None
    df_publicaciones: Optional[pd.DataFrame] = None
    df_libros: Optional[pd.DataFrame] = None

    # Índices pre-calculados para O(1) lookup
    proyectos_count: Dict[str, int] = {}
    publicaciones_count: Dict[str, int] = {}
    libros_count: Dict[str, int] = {}
    roles_by_rut: Dict[str, Set[str]] = {}

    # DataFrames indexados por RUT
    proyectos_by_rut: Dict[str, pd.DataFrame] = {}
    proyectos_extra_by_rut: Dict[str, pd.DataFrame] = {}
    publicaciones_by_rut: Dict[str, pd.DataFrame] = {}
    libros_by_rut: Dict[str, pd.DataFrame] = {}

    # Listas de datos
    publicaciones_list: List[dict] = []
    proyectos_list: List[dict] = []
    investigadores_list: List[dict] = []
    libros_list: List[dict] = []
    
    # Áreas únicas
    all_areas: List[str] = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls, data_directory: str = "./"):
        """
        Carga datos una sola vez.
        
        Args:
            data_directory: Directorio donde están los archivos Excel
        """
        if cls._initialized:
            logger.info("DataCache ya inicializado, reutilizando datos")
            return
        
        logger.info(f"⏳ DataCache: Cargando datos desde {data_directory}...")
        
        try:
            # Construir rutas
            academicas_path = os.path.join(data_directory, ACADEMICAS_FILE)
            proyectos_path = os.path.join(data_directory, PROYECTOS_FILE)
            proyectos_extra_path = os.path.join(data_directory, PROYECTOS_EXTRA_FILE)
            publicaciones_path = os.path.join(data_directory, PUBLICACIONES_FILE)
            libros_path = os.path.join(data_directory, LIBROS_FILE)

            # Verificar archivos
            if not os.path.exists(academicas_path):
                # Intentar sin directorio (para compatibilidad)
                academicas_path = ACADEMICAS_FILE
                proyectos_path = PROYECTOS_FILE
                proyectos_extra_path = PROYECTOS_EXTRA_FILE
                publicaciones_path = PUBLICACIONES_FILE
                libros_path = LIBROS_FILE

            # Cargar DataFrames
            cls.df_academicas = pd.read_excel(academicas_path)
            cls.df_proyectos = pd.read_excel(proyectos_path)
            cls.df_publicaciones = pd.read_excel(publicaciones_path)

            if os.path.exists(proyectos_extra_path):
                cls.df_proyectos_extra = pd.read_excel(proyectos_extra_path)
            else:
                logger.warning(f"⚠️ {PROYECTOS_EXTRA_FILE} no encontrado. Sin enriquecimiento de proyectos.")
                cls.df_proyectos_extra = pd.DataFrame(columns=["rut_ir", "titulo", "fuente", "a_inicio", "a_fin"])

            if os.path.exists(libros_path):
                cls.df_libros = pd.read_excel(libros_path)
            else:
                logger.warning(f"⚠️ Archivo de libros no encontrado: {libros_path}. Se omite.")
                cls.df_libros = pd.DataFrame(columns=["rut_ir", "titulo", "tipo", "editorial", "autores"])

            # Validar columnas requeridas
            required_academicas = {"id", "rut_ir", "name", "ocde_2", "orcid", "grado_mayor"}
            required_proyectos = {"rut_ir", "año", "ocde_2", "rol", "codigo", "titulo"}
            required_publicaciones = {"rut_ir"}
            required_libros = {"rut_ir"}
            cls._validate_columns(cls.df_academicas, required_academicas, "academicas")
            cls._validate_columns(cls.df_proyectos, required_proyectos, "proyectos")
            cls._validate_columns(cls.df_publicaciones, required_publicaciones, "publicaciones")
            cls._validate_columns(cls.df_libros, required_libros, "libros")

            # Limpiar datos
            cls._clean_academicas()
            cls._clean_proyectos()
            cls._clean_proyectos_extra()
            cls._merge_proyectos_extra()
            cls._clean_publicaciones()
            cls._clean_libros()

            # Construir índices
            cls._build_indexes()

            # Convertir a listas
            cls.investigadores_list = cls.df_academicas.to_dict("records")
            cls.publicaciones_list = cls.df_publicaciones.to_dict("records")
            cls.proyectos_list = cls.df_proyectos.to_dict("records")
            cls.libros_list = cls.df_libros.to_dict("records")
            
            cls._data_directory = data_directory
            cls._initialized = True

            logger.info(
                f"✅ DataCache: Cargados {len(cls.investigadores_list)} investigadores, "
                f"{len(cls.publicaciones_list)} publicaciones, "
                f"{len(cls.proyectos_list)} proyectos, "
                f"{len(cls.libros_list)} libros, "
                f"{len(cls.all_areas)} áreas"
            )
            
            # Debug: mostrar estadísticas de conteos
            if cls.publicaciones_count:
                max_pub = max(cls.publicaciones_count.values())
                inv_with_pub = len([v for v in cls.publicaciones_count.values() if v > 0])
                logger.info(f"📊 Publicaciones: máx={max_pub}, investigadores con pub={inv_with_pub}")
            
            if cls.proyectos_count:
                max_proy = max(cls.proyectos_count.values())
                inv_with_proy = len([v for v in cls.proyectos_count.values() if v > 0])
                logger.info(f"📊 Proyectos: máx={max_proy}, investigadores con proy={inv_with_proy}")
            
        except Exception as e:
            logger.error(f"❌ DataCache: Error cargando datos: {e}")
            raise
    
    @classmethod
    def _validate_columns(cls, df: pd.DataFrame, required: set, name: str):
        """Verifica que el DataFrame contenga las columnas mínimas requeridas."""
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Archivo '{name}' no tiene columnas requeridas: {missing}")

    @classmethod
    def _clean_academicas(cls):
        """Limpia y normaliza datos de académicas."""
        df = cls.df_academicas
        df = df.replace("", None)
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"])
        df["id"] = df["id"].astype(int)
        df["orcid"] = df["orcid"].fillna("")
        df["rut_ir"] = df["rut_ir"].astype(str).str.strip().str.upper().str.replace(".", "", regex=False).str.lstrip("0")
        df["grado_mayor"] = df["grado_mayor"].astype(str)
        df["grado_mayor"] = df["grado_mayor"].replace("nan", "INVESTIGADORA")
        df["grado_mayor"] = df["grado_mayor"].replace("", "INVESTIGADORA")
        df["ocde_2"] = (
            df["ocde_2"]
            .astype(str)
            .apply(lambda x: " ,".join(x.split("#")) if x and x != "nan" else "")
        )

        # Dividir 'name' en nombre, apellido1, apellido2
        def _split_name(nombre_completo: str) -> tuple:
            partes = str(nombre_completo).strip().split()
            if len(partes) >= 4:
                return " ".join(partes[:-2]), partes[-2], partes[-1]
            elif len(partes) == 3:
                return partes[0], partes[1], partes[2]
            elif len(partes) == 2:
                return partes[0], partes[1], ""
            else:
                return nombre_completo, "", ""

        df[["nombre", "apellido1", "apellido2"]] = df["name"].apply(
            lambda x: pd.Series(_split_name(x))
        )
        df["nombre"]    = df["nombre"].fillna("").astype(str)
        df["apellido1"] = df["apellido1"].fillna("").astype(str)
        df["apellido2"] = df["apellido2"].fillna("").astype(str)

        cls.df_academicas = df

        # Extraer áreas únicas
        cls.all_areas = sorted(
            df["ocde_2"].dropna().str.split(",").explode().str.strip().unique().tolist()
        )
    
    @classmethod
    def _clean_proyectos(cls):
        """Limpia y normaliza datos de proyectos."""
        df = cls.df_proyectos
        df = df.replace("", np.nan)
        df.columns = df.columns.str.strip()
        df["rut_ir"] = df["rut_ir"].astype(str).str.strip().str.upper().str.replace(".", "", regex=False).str.lstrip("0")
        df["año"] = pd.to_numeric(df["año"], errors="coerce").fillna(0).astype(int)
        df["ocde_2"] = df["ocde_2"].fillna("SIN INFO")
        df["rol"] = df["rol"].fillna("Sin Info")
        cls.df_proyectos = df
    
    @classmethod
    def _clean_proyectos_extra(cls):
        """Limpia y normaliza datos de proyectos.xlsx."""
        df = cls.df_proyectos_extra
        df = df.replace("", np.nan)
        df["rut_ir"] = df["rut_ir"].astype(str).str.strip().str.upper().str.replace(".", "", regex=False).str.lstrip("0")
        for col in ["a_inicio", "a_fin"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").apply(
                    lambda x: str(int(x)) if pd.notna(x) else ""
                )
        if "fuente" in df.columns:
            df["fuente"] = df["fuente"].fillna("").astype(str).str.strip()
        cls.df_proyectos_extra = df

    @classmethod
    def _merge_proyectos_extra(cls):
        """
        Enriquece df_proyectos con fuente/a_inicio/a_fin desde proyectos.xlsx.
        Estrategia: match exacto por (rut_ir, titulo normalizado), luego
        match difuso con SequenceMatcher (cutoff 0.75) dentro del mismo rut.
        """
        import unicodedata
        import re
        from difflib import SequenceMatcher

        def _norm(s: str) -> str:
            s = str(s).strip().lower()
            s = unicodedata.normalize("NFKD", s)
            s = "".join(c for c in s if not unicodedata.combining(c))
            return re.sub(r"\s+", " ", s)

        extra = cls.df_proyectos_extra
        if extra is None or extra.empty:
            cls.df_proyectos["fuente"] = ""
            cls.df_proyectos["a_inicio"] = ""
            cls.df_proyectos["a_fin"] = ""
            return

        extra = extra.copy()
        extra["_norm"] = extra["titulo"].map(_norm)

        # Índice exacto: (rut, titulo_norm) → (fuente, a_inicio, a_fin)
        exact_map: Dict[tuple, tuple] = {}
        # Índice difuso: rut → lista de (titulo_norm, fuente, a_inicio, a_fin)
        fuzzy_map: Dict[str, list] = {}
        for _, row in extra.iterrows():
            rut = str(row["rut_ir"])
            tnorm = row["_norm"]
            vals = (
                str(row.get("fuente", "")),
                str(row.get("a_inicio", "")),
                str(row.get("a_fin", "")),
            )
            exact_map[(rut, tnorm)] = vals
            fuzzy_map.setdefault(rut, []).append((tnorm, *vals))

        CUTOFF = 0.75
        fuentes, inicios, fines = [], [], []

        for _, row in cls.df_proyectos.iterrows():
            rut = str(row["rut_ir"])
            tnorm = _norm(str(row.get("titulo", "")))

            # 1. Match exacto
            if (rut, tnorm) in exact_map:
                f, ai, af = exact_map[(rut, tnorm)]
                fuentes.append(f); inicios.append(ai); fines.append(af)
                continue

            # 2. Match difuso dentro del mismo rut
            candidatos = fuzzy_map.get(rut, [])
            best_ratio, best_vals = 0.0, ("", "", "")
            for cnorm, cf, cai, caf in candidatos:
                ratio = SequenceMatcher(None, tnorm, cnorm).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_vals = (cf, cai, caf)

            if best_ratio >= CUTOFF:
                fuentes.append(best_vals[0])
                inicios.append(best_vals[1])
                fines.append(best_vals[2])
            else:
                fuentes.append(""); inicios.append(""); fines.append("")

        cls.df_proyectos["fuente"] = fuentes
        cls.df_proyectos["a_inicio"] = inicios
        cls.df_proyectos["a_fin"] = fines

        matched = sum(1 for f in fuentes if f)
        logger.info(f"✅ Merge proyectos: {matched}/{len(fuentes)} filas enriquecidas con fuente/período")

    @classmethod
    def _clean_publicaciones(cls):
        """Limpia y normaliza datos de publicaciones."""
        df = cls.df_publicaciones
        df = df.replace("", np.nan)
        df["rut_ir"] = df["rut_ir"].astype(str).str.strip().str.upper().str.replace(".", "", regex=False).str.lstrip("0")
        # Campos de texto: rellenar NaN con cadena vacía
        # Año: solo enteros en rango [1981, año actual], el resto "Sin info"
        import datetime
        current_year = datetime.date.today().year
        if "año" in df.columns:
            años_num = pd.to_numeric(df["año"], errors="coerce")
            df["año"] = años_num.apply(
                lambda x: str(int(x)) if pd.notna(x) and 1981 <= int(x) <= current_year else "Sin info"
            )
        for col in ["titulo", "revista", "autor", "indexacion"]:
            if col in df.columns:
                df[col] = df[col].astype(str).replace("nan", "Sin info")
        cls.df_publicaciones = df

    @classmethod
    def _clean_libros(cls):
        """Limpia y normaliza datos de libros. Separa editorial e ISBN."""
        df = cls.df_libros
        df = df.replace("", np.nan)
        df["rut_ir"] = df["rut_ir"].astype(str).str.strip().str.upper().str.replace(".", "", regex=False).str.lstrip("0")
        for col in ["titulo", "tipo", "autores"]:
            if col in df.columns:
                df[col] = df[col].astype(str).replace("nan", "Sin info")

        # Separar editorial, año e ISBN (formato: "Editorial YYYY , ISBN")
        import re as _re
        _year_pat = _re.compile(r"\s*((?:19|20)\d{2})\s*$")

        def _split_editorial_año_isbn(valor: str):
            if not valor or valor == "nan":
                return "Sin info", "Sin info", "Sin info"
            # Separar ISBN por la coma
            if "," in valor:
                partes = valor.split(",", 1)
                left = partes[0].strip()
                isbn = partes[1].strip().removeprefix("ISBN").strip() or "Sin info"
            else:
                left = valor.strip()
                isbn = "Sin info"
            # Extraer año del lado izquierdo
            m = _year_pat.search(left)
            if m:
                año = m.group(1)
                editorial = _year_pat.sub("", left).strip(" .,") or "Sin info"
            else:
                año = "Sin info"
                editorial = left or "Sin info"
            return editorial, año, isbn

        if "editorial" in df.columns and not df.empty:
            df[["editorial", "año", "isbn"]] = df["editorial"].astype(str).apply(
                lambda x: pd.Series(_split_editorial_año_isbn(x))
            )
        else:
            if "editorial" not in df.columns:
                df["editorial"] = "Sin info"
            df["año"] = "Sin info"
            df["isbn"] = "Sin info"

        cls.df_libros = df

    @classmethod
    def _build_indexes(cls):
        """Construye índices para acceso O(1)."""
        # Conteos por RUT - convertir claves a string para consistencia
        proyectos_grouped = cls.df_proyectos.groupby("rut_ir").size()
        cls.proyectos_count = {str(k): v for k, v in proyectos_grouped.to_dict().items()}
        
        publicaciones_grouped = cls.df_publicaciones.groupby("rut_ir").size()
        cls.publicaciones_count = {str(k): v for k, v in publicaciones_grouped.to_dict().items()}
        
        # Roles por RUT
        cls.roles_by_rut = {}
        for rut, group in cls.df_proyectos.groupby("rut_ir"):
            roles = set(group["rol"].dropna().str.lower().str.strip())
            cls.roles_by_rut[str(rut)] = roles
        
        # DataFrames por RUT (para carga bajo demanda)
        cls.proyectos_by_rut = {}
        for rut, group in cls.df_proyectos.groupby("rut_ir"):
            cls.proyectos_by_rut[str(rut)] = group.copy()
        
        cls.publicaciones_by_rut = {}
        for rut, group in cls.df_publicaciones.groupby("rut_ir"):
            cls.publicaciones_by_rut[str(rut)] = group.copy()

        libros_grouped = cls.df_libros.groupby("rut_ir").size()
        cls.libros_count = {str(k): v for k, v in libros_grouped.to_dict().items()}

        cls.libros_by_rut = {}
        for rut, group in cls.df_libros.groupby("rut_ir"):
            cls.libros_by_rut[str(rut)] = group.copy()

        cls.proyectos_extra_by_rut = {}
        if cls.df_proyectos_extra is not None and not cls.df_proyectos_extra.empty:
            for rut, group in cls.df_proyectos_extra.groupby("rut_ir"):
                cls.proyectos_extra_by_rut[str(rut)] = group.copy()

    @classmethod
    def is_initialized(cls) -> bool:
        """Verifica si el caché está inicializado."""
        return cls._initialized

    @classmethod
    def reload_publicaciones(cls) -> int:
        """
        Recarga publicaciones_total.xlsx sin reiniciar el servidor.
        Devuelve el número de registros cargados.
        """
        pub_path = os.path.join(cls._data_directory, PUBLICACIONES_FILE)
        if not os.path.exists(pub_path):
            pub_path = PUBLICACIONES_FILE

        cls.df_publicaciones = pd.read_excel(pub_path)
        cls._validate_columns(cls.df_publicaciones, {"rut_ir"}, "publicaciones")
        cls._clean_publicaciones()

        # Reconstruir solo índices de publicaciones
        publicaciones_grouped = cls.df_publicaciones.groupby("rut_ir").size()
        cls.publicaciones_count = {str(k): v for k, v in publicaciones_grouped.to_dict().items()}
        cls.publicaciones_by_rut = {}
        for rut, group in cls.df_publicaciones.groupby("rut_ir"):
            cls.publicaciones_by_rut[str(rut)] = group.copy()
        cls.publicaciones_list = cls.df_publicaciones.to_dict("records")

        total = len(cls.publicaciones_list)
        logger.info(f"✅ Publicaciones recargadas: {total} registros")
        return total

    @classmethod
    def get_proyectos_count(cls, rut_ir) -> int:
        """O(1) lookup de conteo de proyectos."""
        return cls.proyectos_count.get(str(rut_ir), 0)
    
    @classmethod
    def get_publicaciones_count(cls, rut_ir) -> int:
        """O(1) lookup de conteo de publicaciones."""
        return cls.publicaciones_count.get(str(rut_ir), 0)

    @classmethod
    def get_libros_count(cls, rut_ir) -> int:
        """O(1) lookup de conteo de libros."""
        return cls.libros_count.get(str(rut_ir), 0)
    
    @classmethod
    def has_rol(cls, rut_ir, search_rol: str) -> bool:
        """O(1) verificación de rol."""
        roles = cls.roles_by_rut.get(str(rut_ir), set())
        search_lower = search_rol.lower()
        
        rol_mapping = {
            "ir": ["investigador responsable", "responsable"],
            "co-i": ["co-investigador", "coinvestigador", "co investigador"],
        }
        
        terms = rol_mapping.get(search_lower, [search_lower])
        
        for role in roles:
            for term in terms:
                if term in role:
                    return True
        return False
    
    @classmethod
    def get_proyectos_by_rut(cls, rut: str) -> pd.DataFrame:
        """Obtiene DataFrame de proyectos por RUT."""
        return cls.proyectos_by_rut.get(str(rut), pd.DataFrame())
    
    @classmethod
    def get_publicaciones_by_rut(cls, rut: str) -> pd.DataFrame:
        """Obtiene DataFrame de publicaciones por RUT."""
        return cls.publicaciones_by_rut.get(str(rut), pd.DataFrame())

    @classmethod
    def get_libros_by_rut(cls, rut: str) -> pd.DataFrame:
        """Obtiene DataFrame de libros por RUT."""
        return cls.libros_by_rut.get(str(rut), pd.DataFrame())

    @classmethod
    def get_proyectos_extra_by_rut(cls, rut: str) -> pd.DataFrame:
        """Obtiene DataFrame de proyectos.xlsx por RUT."""
        return cls.proyectos_extra_by_rut.get(str(rut), pd.DataFrame())


# Instancia singleton (para imports más limpios)
data_cache = DataCache()