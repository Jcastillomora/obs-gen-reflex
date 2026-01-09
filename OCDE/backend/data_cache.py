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
ACADEMICAS_FILE = "academicas.xlsx"
PUBLICACIONES_FILE = "publicaciones_total.xlsx"


class DataCache:
    """
    Singleton para caché de datos compartido.
    Se inicializa UNA sola vez y es usado por todo el sistema.
    """
    _instance: Optional['DataCache'] = None
    _initialized: bool = False
    
    # DataFrames cargados
    df_academicas: Optional[pd.DataFrame] = None
    df_proyectos: Optional[pd.DataFrame] = None
    df_publicaciones: Optional[pd.DataFrame] = None
    
    # Índices pre-calculados para O(1) lookup
    proyectos_count: Dict[str, int] = {}
    publicaciones_count: Dict[str, int] = {}
    roles_by_rut: Dict[str, Set[str]] = {}
    
    # DataFrames indexados por RUT
    proyectos_by_rut: Dict[str, pd.DataFrame] = {}
    publicaciones_by_rut: Dict[str, pd.DataFrame] = {}
    
    # Listas de datos
    publicaciones_list: List[dict] = []
    proyectos_list: List[dict] = []
    investigadores_list: List[dict] = []
    
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
            publicaciones_path = os.path.join(data_directory, PUBLICACIONES_FILE)
            
            # Verificar archivos
            if not os.path.exists(academicas_path):
                # Intentar sin directorio (para compatibilidad)
                academicas_path = ACADEMICAS_FILE
                proyectos_path = PROYECTOS_FILE
                publicaciones_path = PUBLICACIONES_FILE
            
            # Cargar DataFrames
            cls.df_academicas = pd.read_excel(academicas_path)
            cls.df_proyectos = pd.read_excel(proyectos_path)
            cls.df_publicaciones = pd.read_excel(publicaciones_path)
            
            # Limpiar datos
            cls._clean_academicas()
            cls._clean_proyectos()
            cls._clean_publicaciones()
            
            # Construir índices
            cls._build_indexes()
            
            # Convertir a listas
            cls.investigadores_list = cls.df_academicas.to_dict("records")
            cls.publicaciones_list = cls.df_publicaciones.to_dict("records")
            cls.proyectos_list = cls.df_proyectos.to_dict("records")
            
            cls._initialized = True
            
            logger.info(
                f"✅ DataCache: Cargados {len(cls.investigadores_list)} investigadores, "
                f"{len(cls.publicaciones_list)} publicaciones, "
                f"{len(cls.proyectos_list)} proyectos, "
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
    def _clean_academicas(cls):
        """Limpia y normaliza datos de académicas."""
        df = cls.df_academicas
        df = df.replace("", None)
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"])
        df["id"] = df["id"].astype(int)
        df["orcid"] = df["orcid"].fillna("")
        df["grado_mayor"] = df["grado_mayor"].astype(str)
        df["grado_mayor"] = df["grado_mayor"].replace("nan", "INVESTIGADORA")
        df["grado_mayor"] = df["grado_mayor"].replace("", "INVESTIGADORA")
        df["ocde_2"] = (
            df["ocde_2"]
            .astype(str)
            .apply(lambda x: " ,".join(x.split("#")) if x and x != "nan" else "")
        )
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
        df["año"] = pd.to_numeric(df["año"], errors="coerce").fillna(0).astype(int)
        df["ocde_2"] = df["ocde_2"].fillna("SIN INFO")
        df["rol"] = df["rol"].fillna("Sin Info")
        cls.df_proyectos = df
    
    @classmethod
    def _clean_publicaciones(cls):
        """Limpia y normaliza datos de publicaciones."""
        df = cls.df_publicaciones
        df = df.replace("", np.nan)
        df["doi"] = df["doi"].astype(str).replace("nan", "")
        cls.df_publicaciones = df
    
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
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Verifica si el caché está inicializado."""
        return cls._initialized
    
    @classmethod
    def get_proyectos_count(cls, rut_ir) -> int:
        """O(1) lookup de conteo de proyectos."""
        return cls.proyectos_count.get(str(rut_ir), 0)
    
    @classmethod
    def get_publicaciones_count(cls, rut_ir) -> int:
        """O(1) lookup de conteo de publicaciones."""
        return cls.publicaciones_count.get(str(rut_ir), 0)
    
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


# Instancia singleton (para imports más limpios)
data_cache = DataCache()