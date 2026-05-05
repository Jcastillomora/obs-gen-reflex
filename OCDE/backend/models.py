import reflex as rx
from typing import Optional, List
from datetime import datetime

# modelo de la base de datos para los investigadores
class Investigador(rx.Base):
    id: int
    rut_ir: str
    nombre: str
    apellido1: str
    apellido2: str = ""
    orcid: Optional[str] = None
    ocde_2: Optional[str] = None
    ocde_3: Optional[str] = None
    email: Optional[str] = None
    grado_mayor: Optional[str] = None
    unidad_contrato: Optional[str] = None
    total_proyectos: int = 0
    total_publicaciones: int = 0
    # titulo: Optional[str] = None
    # magister: Optional[str] = None
    # doctorado: Optional[str] = None
    # programa: Optional[str] = None
    # linea: Optional[str] = None

# modelo de la base de datos para las publicaciones
class Publicaciones(rx.Base):
    año: str = "Sin info"
    titulo: str = "Sin info"
    revista: str = "Sin info"
    # cuartil: str
    rut_ir: str = ""
    # genero: str
    autor: str = "Sin info"
    # wos_id: str
    # liderado: str
    indexacion: str = "Sin info"
    # url: str
    # doi: str

# modelo de la base de datos para los proyectos
class Proyectos(rx.Base):
    codigo: str
    titulo: str
    año: str
    ocde_2: str
    tipo_proyecto: str
    investigador_responsable: str
    rut_ir: str
    rol: str


# modelo SQLite para documentos del repositorio
class Documento(rx.Model, table=True):
    titulo: str
    descripcion: str
    tipo: str           # "reporte" | "documento"
    filename: str       # nombre del archivo en assets/uploads/
    created_at: str = ""
