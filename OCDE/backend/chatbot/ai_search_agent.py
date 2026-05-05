# ai_search_agent.py - Versión mejorada con Agno tools + output_schema
"""
AI Search Agent usando Agno framework para búsqueda inteligente.
OPTIMIZADO: Usa DataCache compartido + @tool functions + Pydantic output_schema.

UBICACIÓN: OCDE/backend/chatbot/ai_search_agent.py
"""

import os
import logging
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.decorator import tool

# Importar caché compartido
try:
    from ..data_cache import DataCache
    USE_SHARED_CACHE = True
except ImportError:
    USE_SHARED_CACHE = False
    import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del agente
AI_MODEL_ID = "claude-haiku-4-5-20251001"


# =========================================================
# MODELO PYDANTIC PARA SALIDA ESTRUCTURADA
# =========================================================

class SearchResult(BaseModel):
    tipo_busqueda: str = Field(
        ...,
        description="Tipo detectado: nombre | area | titulo | filtro_numerico | rol | hibrida"
    )
    areas_detectadas: List[str] = Field(
        default_factory=list,
        description="Áreas OCDE detectadas (usar nombres exactos de listar_areas_ocde)"
    )
    nombres_detectados: List[str] = Field(
        default_factory=list,
        description="Nombres completos de investigadoras detectados"
    )
    titulos_detectados: List[str] = Field(
        default_factory=list,
        description="Fragmentos de títulos de publicaciones o proyectos"
    )
    terminos_busqueda: List[str] = Field(
        default_factory=list,
        description="Términos generales para búsqueda de texto"
    )
    min_proyectos: Optional[int] = Field(
        None,
        description="Cantidad mínima de proyectos requerida (null si no aplica)"
    )
    min_publicaciones: Optional[int] = Field(
        None,
        description="Cantidad mínima de publicaciones requerida (null si no aplica)"
    )
    rol_filtro: Optional[str] = Field(
        None,
        description="Filtro de rol: 'ir' (investigadora responsable) o 'co-i' (co-investigadora)"
    )
    resumen: str = Field(
        "",
        description="Explicación breve de qué se buscó y cuántos resultados hay"
    )


# =========================================================
# HERRAMIENTAS @tool QUE ACCEDEN AL DATACACHE
# =========================================================

@tool
def listar_areas_ocde() -> str:
    """Lista todas las áreas OCDE disponibles en el repositorio.
    Úsala para verificar nombres exactos de áreas antes de incluirlas en areas_detectadas.
    """
    if not USE_SHARED_CACHE or not DataCache.is_initialized():
        return "Datos no disponibles"
    areas = DataCache.all_areas
    return f"Áreas OCDE disponibles ({len(areas)}):\n" + "\n".join(f"- {a}" for a in areas)


@tool
def buscar_investigadoras_por_nombre(nombre: str) -> str:
    """Busca investigadoras cuyo nombre o apellido contenga el texto dado.
    Retorna nombre completo, ID, conteos de publicaciones y proyectos.

    Args:
        nombre: Nombre o fragmento de nombre a buscar (insensible a mayúsculas).
    """
    if not USE_SHARED_CACHE or not DataCache.is_initialized():
        return "Datos no disponibles"

    nombre_lower = nombre.lower()
    resultados = []
    for inv in DataCache.investigadores_list:
        nombre_completo = (
            f"{inv.get('nombre', '')} {inv.get('apellido1', '')} {inv.get('apellido2', '')}".strip()
        )
        if nombre_lower in nombre_completo.lower():
            rut = inv.get("rut_ir", "")
            pubs = DataCache.get_publicaciones_count(rut)
            proyectos = DataCache.get_proyectos_count(rut)
            resultados.append(
                f"- {nombre_completo} (ID: {inv.get('id')}, Pub: {pubs}, Proy: {proyectos})"
            )

    if not resultados:
        return f"No se encontraron investigadoras con nombre '{nombre}'"
    return f"Investigadoras encontradas ({len(resultados)}):\n" + "\n".join(resultados[:20])


@tool
def buscar_investigadoras_por_area(area: str) -> str:
    """Busca investigadoras que trabajen en un área OCDE específica.
    Retorna lista de nombres con sus áreas.

    Args:
        area: Nombre o fragmento del área OCDE a buscar (insensible a mayúsculas).
    """
    if not USE_SHARED_CACHE or not DataCache.is_initialized():
        return "Datos no disponibles"

    area_lower = area.lower()
    resultados = []
    for inv in DataCache.investigadores_list:
        ocde = str(inv.get("ocde_2", ""))
        if area_lower in ocde.lower():
            nombre = (
                f"{inv.get('nombre', '')} {inv.get('apellido1', '')} {inv.get('apellido2', '')}".strip()
            )
            resultados.append(f"- {nombre} | Áreas: {ocde[:100]}")

    if not resultados:
        return f"No se encontraron investigadoras en el área '{area}'"
    return f"Investigadoras en área '{area}' ({len(resultados)} encontradas):\n" + "\n".join(resultados[:20])


@tool
def buscar_publicacion_por_titulo(fragmento: str) -> str:
    """Busca publicaciones cuyo título contenga el texto dado y retorna las investigadoras asociadas.

    Args:
        fragmento: Fragmento del título de la publicación (insensible a mayúsculas).
    """
    if not USE_SHARED_CACHE or not DataCache.is_initialized():
        return "Datos no disponibles"

    fragmento_lower = fragmento.lower()
    resultados = []
    ruts_vistos: set = set()

    # Construir índice rut → nombre
    rut_a_nombre = {
        inv.get("rut_ir", ""): (
            f"{inv.get('nombre', '')} {inv.get('apellido1', '')} {inv.get('apellido2', '')}".strip()
        )
        for inv in DataCache.investigadores_list
    }

    for pub in DataCache.publicaciones_list:
        titulo = str(pub.get("titulo", "")).lower()
        if fragmento_lower in titulo:
            rut = pub.get("rut_ir", "")
            if rut not in ruts_vistos:
                nombre = rut_a_nombre.get(rut, f"RUT {rut}")
                resultados.append(f"- {nombre}: '{pub.get('titulo', '')[:100]}'")
                ruts_vistos.add(rut)

    if not resultados:
        return f"No se encontraron publicaciones con '{fragmento}'"
    return f"Publicaciones encontradas ({len(resultados)}):\n" + "\n".join(resultados[:15])


@tool
def buscar_proyecto_por_titulo(fragmento: str) -> str:
    """Busca proyectos cuyo título contenga el texto dado y retorna las investigadoras asociadas.

    Args:
        fragmento: Fragmento del título del proyecto (insensible a mayúsculas).
    """
    if not USE_SHARED_CACHE or not DataCache.is_initialized():
        return "Datos no disponibles"

    fragmento_lower = fragmento.lower()
    resultados = []
    ruts_vistos: set = set()

    rut_a_nombre = {
        inv.get("rut_ir", ""): (
            f"{inv.get('nombre', '')} {inv.get('apellido1', '')} {inv.get('apellido2', '')}".strip()
        )
        for inv in DataCache.investigadores_list
    }

    for proy in DataCache.proyectos_list:
        titulo = str(proy.get("titulo", "")).lower()
        if fragmento_lower in titulo:
            rut = proy.get("rut_ir", "")
            if rut not in ruts_vistos:
                nombre = rut_a_nombre.get(rut, f"RUT {rut}")
                resultados.append(f"- {nombre}: '{proy.get('titulo', '')[:100]}'")
                ruts_vistos.add(rut)

    if not resultados:
        return f"No se encontraron proyectos con '{fragmento}'"
    return f"Proyectos encontrados ({len(resultados)}):\n" + "\n".join(resultados[:15])


@tool
def buscar_por_termino_libre(termino: str) -> str:
    """Búsqueda semántica amplia: busca el término en grado académico, títulos de publicaciones y proyectos.
    Úsala cuando la consulta describe una línea de investigación o tema que puede no coincidir con áreas OCDE exactas.
    Retorna nombres e IDs (sin datos de identificación personal) ordenados por relevancia.

    Args:
        termino: Término o frase a buscar (ej: "biología celular", "salud mental", "cambio climático").
    """
    if not USE_SHARED_CACHE or not DataCache.is_initialized():
        return "Datos no disponibles"

    termino_lower = termino.lower()
    id_scores: dict = {}
    id_a_inv: dict = {}

    # Indexar por ID público (no por RUT)
    for inv in DataCache.investigadores_list:
        inv_id = inv.get("id")
        rut = inv.get("rut_ir", "")
        if inv_id:
            id_a_inv[inv_id] = inv

        # Buscar en grado_mayor (peso 2)
        grado = str(inv.get("grado_mayor", "")).lower()
        if termino_lower in grado:
            id_scores[inv_id] = id_scores.get(inv_id, 0) + 2

    # Buscar en títulos de publicaciones (peso 1)
    rut_a_id = {inv.get("rut_ir", ""): inv.get("id") for inv in DataCache.investigadores_list}
    for pub in DataCache.publicaciones_list:
        rut = pub.get("rut_ir", "")
        titulo = str(pub.get("titulo", "")).lower()
        inv_id = rut_a_id.get(rut)
        if termino_lower in titulo and inv_id:
            id_scores[inv_id] = id_scores.get(inv_id, 0) + 1

    # Buscar en títulos de proyectos (peso 1)
    for proy in DataCache.proyectos_list:
        rut = proy.get("rut_ir", "")
        titulo = str(proy.get("titulo", "")).lower()
        inv_id = rut_a_id.get(rut)
        if termino_lower in titulo and inv_id:
            id_scores[inv_id] = id_scores.get(inv_id, 0) + 1

    if not id_scores:
        return f"No se encontraron resultados para '{termino}' en grado académico, publicaciones o proyectos."

    sorted_ids = sorted(id_scores.items(), key=lambda x: x[1], reverse=True)

    resultados = []
    for inv_id, score in sorted_ids[:30]:
        inv = id_a_inv.get(inv_id, {})
        nombre = f"{inv.get('nombre', '')} {inv.get('apellido1', '')} {inv.get('apellido2', '')}".strip()
        pubs = DataCache.get_publicaciones_count(inv.get("rut_ir", ""))
        proyectos = DataCache.get_proyectos_count(inv.get("rut_ir", ""))
        resultados.append(f"- {nombre} (ID: {inv_id}, Pub: {pubs}, Proy: {proyectos}, Relevancia: {score})")

    return (
        f"Investigadoras relevantes para '{termino}' ({len(id_scores)} encontradas):\n"
        + "\n".join(resultados)
    )


@tool
def obtener_estadisticas() -> str:
    """Obtiene estadísticas generales del repositorio: totales de investigadoras, publicaciones y proyectos."""
    if not USE_SHARED_CACHE or not DataCache.is_initialized():
        return "Datos no disponibles"
    return (
        f"Total investigadoras: {len(DataCache.investigadores_list)}\n"
        f"Total publicaciones: {len(DataCache.publicaciones_list)}\n"
        f"Total proyectos: {len(DataCache.proyectos_list)}\n"
        f"Total áreas OCDE: {len(DataCache.all_areas)}"
    )


# =========================================================
# CLASE PRINCIPAL DEL AGENTE
# =========================================================

class AgnoSearchAgent:
    """
    AI Search Agent usando Agno framework para búsqueda inteligente.
    Usa @tool functions para acceder al DataCache completo y output_schema
    para retornar resultados estructurados sin parsing manual.
    """

    def __init__(self, data_directory: str = "./"):
        self.data_directory = data_directory
        self.agent: Optional[Agent] = None
        self.investigadores_data = []
        self.all_areas = []
        self._initialize()

    def _initialize(self):
        """Inicializa Agno Agent con Claude."""
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY no configurada")
                return

            self._load_data()

            if not self.investigadores_data:
                logger.warning("No se encontraron datos de investigadores válidos")
                return

            self._create_agent()
            logger.info("Agno Search Agent inicializado correctamente")

        except Exception as e:
            logger.error(f"Error inicializando Agno Search Agent: {e}")

    def _load_data(self):
        """Carga datos desde DataCache compartido o archivos como fallback."""
        try:
            if USE_SHARED_CACHE:
                self._load_from_shared_cache()
            else:
                self._load_from_files()
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            if USE_SHARED_CACHE:
                logger.info("Intentando fallback a carga directa de archivos...")
                self._load_from_files()

    def _load_from_shared_cache(self):
        """Carga datos desde el DataCache compartido."""
        logger.info("📦 Usando DataCache compartido")

        if not DataCache.is_initialized():
            DataCache.initialize(self.data_directory)

        self.investigadores_data = DataCache.investigadores_list
        self.all_areas = DataCache.all_areas

        logger.info(
            f"Cargados desde caché: {len(self.investigadores_data)} investigadores, "
            f"{len(DataCache.publicaciones_list)} publicaciones, "
            f"{len(DataCache.proyectos_list)} proyectos, "
            f"{len(self.all_areas)} áreas"
        )

    def _load_from_files(self):
        """Carga datos directamente desde archivos Excel (fallback)."""
        logger.info("📄 Cargando datos desde archivos Excel")

        import pandas as pd

        academicas_file = os.path.join(self.data_directory, "academicas.xlsx")
        if not os.path.exists(academicas_file):
            logger.error(f"Archivo {academicas_file} no encontrado")
            return

        df_academicas = pd.read_excel(academicas_file)
        df_academicas = df_academicas.replace("", None)
        df_academicas["id"] = pd.to_numeric(df_academicas["id"], errors="coerce")
        df_academicas = df_academicas.dropna(subset=["id"])
        df_academicas["id"] = df_academicas["id"].astype(int)
        df_academicas["orcid"] = df_academicas["orcid"].fillna("")
        df_academicas["grado_mayor"] = (
            df_academicas["grado_mayor"].astype(str).replace("nan", "INVESTIGADORA")
        )
        df_academicas["ocde_2"] = (
            df_academicas["ocde_2"]
            .astype(str)
            .apply(lambda x: ", ".join(x.split("#")) if x and x != "nan" else "")
        )

        self.all_areas = sorted(
            df_academicas["ocde_2"]
            .dropna()
            .str.split(",")
            .explode()
            .str.strip()
            .unique()
            .tolist()
        )
        self.investigadores_data = df_academicas.to_dict("records")

        logger.info(
            f"Cargados desde archivos: {len(self.investigadores_data)} investigadores, "
            f"{len(self.all_areas)} áreas"
        )

    def _create_agent(self):
        """Crea el agente Agno con tools. Respuesta JSON validada con Pydantic."""
        try:
            self.agent = Agent(
                model=Claude(id=AI_MODEL_ID),
                description="Agente de búsqueda inteligente para el repositorio de investigadoras OCDE-UFRO.",
                instructions=[
                    "Eres un asistente especializado en búsqueda de investigadoras del Observatorio de Género en Ciencia de la Universidad de La Frontera (UFRO).",
                    "Analiza la consulta y usa las herramientas disponibles para buscar en los datos reales antes de responder.",
                    "FLUJO DE BÚSQUEDA RECOMENDADO:",
                    "1. Para consultas de nombre → usa buscar_investigadoras_por_nombre().",
                    "2. Para consultas de área → usa listar_areas_ocde() para obtener nombres exactos, luego buscar_investigadoras_por_area().",
                    "3. Para líneas de investigación o temas que NO son áreas OCDE exactas (ej: 'biología celular', 'salud mental', 'género y ciencia') → usa buscar_por_termino_libre() y copia los términos en terminos_busqueda.",
                    "4. Para consultas de título específico → usa buscar_publicacion_por_titulo() o buscar_proyecto_por_titulo().",
                    "REGLA IMPORTANTE: Si la consulta describe una temática o línea de investigación, SIEMPRE usa buscar_por_termino_libre() y coloca los términos clave en terminos_busqueda.",
                    "Detecta tipo de búsqueda: nombre | area | titulo | filtro_numerico | rol | hibrida.",
                    "Filtros numéricos: 'más de 20 publicaciones' → min_publicaciones=20, 'al menos 5 proyectos' → min_proyectos=5.",
                    "Roles: 'investigadora responsable'/'IR' → rol_filtro='ir'; 'co-investigadora'/'co-i' → rol_filtro='co-i'.",
                    "El campo 'resumen' debe ser una frase breve y natural. NUNCA incluyas IDs, RUTs ni números de identificación en el resumen. Solo menciona nombres, áreas y cantidades.",
                    """Tu respuesta FINAL debe ser ÚNICAMENTE un objeto JSON válido con esta estructura exacta (sin texto adicional, sin markdown):
{"tipo_busqueda":"area","areas_detectadas":[],"nombres_detectados":[],"titulos_detectados":[],"terminos_busqueda":[],"min_proyectos":null,"min_publicaciones":null,"rol_filtro":null,"resumen":""}""",
                ],
                tools=[
                    listar_areas_ocde,
                    buscar_investigadoras_por_nombre,
                    buscar_investigadoras_por_area,
                    buscar_por_termino_libre,
                    buscar_publicacion_por_titulo,
                    buscar_proyecto_por_titulo,
                    obtener_estadisticas,
                ],
                tool_call_limit=8,
                retries=2,
                telemetry=False,
                markdown=False,
            )
            logger.info("Agno Agent creado exitosamente")

        except Exception as e:
            logger.error(f"Error creando agent: {e}")

    def search(self, query: str) -> Dict[str, Any]:
        """
        Realiza búsqueda inteligente usando el agente.

        Args:
            query: Consulta en lenguaje natural

        Returns:
            Dict con resultados estructurados
        """
        import json

        try:
            if not self.agent:
                return self._fallback_search(query)

            if not query.strip():
                return {"error": "Consulta vacía"}

            response = self.agent.run(query)
            response_text = str(response.content) if hasattr(response, "content") else str(response)

            # Extraer JSON del texto de respuesta
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start == -1 or end == 0:
                logger.warning("No se encontró JSON en la respuesta del agente")
                return self._fallback_search(query)

            data = json.loads(response_text[start:end])

            # Validar con Pydantic y filtrar áreas
            result = SearchResult.model_validate(data)
            result.areas_detectadas = [
                area for area in result.areas_detectadas
                if area in self.all_areas
            ]
            return result.model_dump()

        except Exception as e:
            logger.error(f"Error en búsqueda inteligente: {e}")
            return self._fallback_search(query)

    def _fallback_search(self, query: str) -> Dict[str, Any]:
        """Búsqueda de respaldo cuando el agente no está disponible."""
        try:
            import re
            query_lower = query.lower()

            detected_areas = [
                area for area in self.all_areas
                if any(word in area.lower() for word in query_lower.split())
            ]
            search_terms = [w for w in query_lower.split() if len(w) > 2]

            min_proyectos = None
            min_publicaciones = None
            rol_filtro = None

            proy_match = re.search(r"(?:más|mas)\s+de\s+(\d+)\s*proyectos?", query_lower)
            if proy_match:
                min_proyectos = int(proy_match.group(1))

            pub_match = re.search(r"(?:más|mas)\s+de\s+(\d+)\s*(?:publicaciones?|papers?)", query_lower)
            if pub_match:
                min_publicaciones = int(pub_match.group(1))

            if re.search(r"(?:co-?i\b|co-?\s*investigador)", query_lower):
                rol_filtro = "co-i"
            elif re.search(r"(?:\bir\b|responsables?)", query_lower):
                rol_filtro = "ir"

            tipo = "area"
            if min_proyectos or min_publicaciones:
                tipo = "filtro_numerico"
            elif rol_filtro:
                tipo = "rol"

            return {
                "tipo_busqueda": tipo,
                "areas_detectadas": detected_areas[:5],
                "nombres_detectados": [],
                "titulos_detectados": [],
                "terminos_busqueda": search_terms[:5],
                "min_proyectos": min_proyectos,
                "min_publicaciones": min_publicaciones,
                "rol_filtro": rol_filtro,
                "resumen": f"Búsqueda simple por '{query}'. {len(detected_areas)} áreas relacionadas detectadas.",
            }

        except Exception as e:
            logger.error(f"Error en búsqueda de respaldo: {e}")
            return {
                "tipo_busqueda": "area",
                "areas_detectadas": [],
                "nombres_detectados": [],
                "titulos_detectados": [],
                "terminos_busqueda": [],
                "min_proyectos": None,
                "min_publicaciones": None,
                "rol_filtro": None,
                "resumen": f"Error en la búsqueda: {str(e)}",
            }

    def is_ready(self) -> bool:
        """Verifica si el agente está listo."""
        return self.agent is not None and len(self.investigadores_data) > 0

    def get_agent_info(self) -> Dict[str, Any]:
        """Obtiene información sobre el estado del agente."""
        return {
            "ready": self.is_ready(),
            "investigadores_loaded": len(self.investigadores_data),
            "areas_available": len(self.all_areas),
            "model": AI_MODEL_ID,
            "framework": "Agno + output_schema + @tool",
            "uses_shared_cache": USE_SHARED_CACHE,
            "data_directory": self.data_directory,
        }


# =========================================================
# INSTANCIA SINGLETON + FUNCIONES DE UTILIDAD
# =========================================================

search_agent = AgnoSearchAgent()


def get_ai_search_response(query: str) -> Dict[str, Any]:
    """Función de utilidad para búsqueda inteligente."""
    return search_agent.search(query)


def is_ai_search_ready() -> bool:
    """Función de utilidad para verificar si el agente está listo."""
    return search_agent.is_ready()


def get_ai_search_info() -> Dict[str, Any]:
    """Función de utilidad para obtener información del agente."""
    return search_agent.get_agent_info()


def get_available_areas() -> List[str]:
    """Función de utilidad para obtener áreas disponibles."""
    return search_agent.all_areas


if __name__ == "__main__":
    print("=== AI Search Agent con Agno Framework (output_schema + @tool) ===")
    info = get_ai_search_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    if is_ai_search_ready():
        print("\n¡Agente de búsqueda listo!")

        test_queries = [
            "busca investigadoras de matemáticas",
            "encuentra expertas en biotecnología",
            "investigadoras con más de 20 publicaciones",
            "investigadoras responsables en psicología",
        ]

        for query in test_queries:
            print(f"\nConsulta: {query}")
            result = get_ai_search_response(query)
            print(f"Tipo: {result.get('tipo_busqueda')}")
            print(f"Áreas detectadas: {result.get('areas_detectadas', [])}")
            print(f"Resumen: {result.get('resumen', '')[:100]}")
    else:
        print("\nAgente no está listo. Verifica ANTHROPIC_API_KEY.")
