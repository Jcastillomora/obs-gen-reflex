import reflex as rx
from typing import Optional

# modelo de la base de datos para los investigadores
class Investigador(rx.Base):
    id: int
    rut_ir: str
    name: str
    orcid: Optional[str] = None
    ocde_2: str
    ocde_3: Optional[str] = None
    email: Optional[str] = None
    grado_mayor: Optional[str] = None
    unidad_contrato: Optional[str] = None
    # titulo: Optional[str] = None
    # magister: Optional[str] = None
    # doctorado: Optional[str] = None
    # programa: Optional[str] = None
    # linea: Optional[str] = None

# modelo de la base de datos para las publicaciones
class Publicaciones(rx.Base):
    año: str
    titulo: str
    revista: str
    cuartil: str
    rut_ir: str
    genero: str
    autor: str
    wos_id: str
    liderado: str
    url: str
    doi: str

# modelo de la base de datos para los proyectos
class Proyectos(rx.Base):
    """Proyectos class."""

    codigo: str
    titulo: str
    año: str
    ocde_1: str
    ocde_2: str
    tipo_proyecto: str
    investigador_responsable: str
    rut_ir: str
    rol: str
    