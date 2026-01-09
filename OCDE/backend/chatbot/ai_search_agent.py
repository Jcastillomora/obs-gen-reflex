# ai_search_agent.py - Versión optimizada con caché compartido
"""
AI Search Agent usando Agno framework para búsqueda inteligente.
OPTIMIZADO: Usa DataCache compartido para evitar cargar Excel dos veces.

UBICACIÓN: OCDE/backend/chatbot/ai_search_agent.py
"""

import os
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent
from agno.models.anthropic import Claude

# Importar caché compartido
try:
    from ..data_cache import DataCache
    USE_SHARED_CACHE = True
except ImportError:
    # Fallback si no se puede importar
    USE_SHARED_CACHE = False
    import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgnoSearchAgent:
    """
    AI Search Agent usando Agno framework para búsqueda inteligente.
    OPTIMIZADO: Usa DataCache compartido cuando está disponible.
    """

    def __init__(self, data_directory: str = "./"):
        """
        Inicializa el agente de búsqueda con Agno.

        Args:
            data_directory: Directorio que contiene los archivos de datos
        """
        self.data_directory = data_directory
        self.agent: Optional[Agent] = None
        self.investigadores_data = []
        self.all_areas = []
        self.investigadores_summary = ""
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
        """
        Carga y procesa datos de investigadores.
        OPTIMIZADO: Usa DataCache compartido si está disponible.
        """
        try:
            if USE_SHARED_CACHE:
                self._load_from_shared_cache()
            else:
                self._load_from_files()
                
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            # Intentar fallback a archivos
            if USE_SHARED_CACHE:
                logger.info("Intentando fallback a carga directa de archivos...")
                self._load_from_files()

    def _load_from_shared_cache(self):
        """Carga datos desde el DataCache compartido."""
        logger.info("📦 Usando DataCache compartido")
        
        # Inicializar caché si no está listo
        if not DataCache.is_initialized():
            DataCache.initialize(self.data_directory)
        
        # Usar datos del caché
        self.investigadores_data = DataCache.investigadores_list
        self.all_areas = DataCache.all_areas
        
        # Crear resumen extendido
        self._create_investigators_summary_from_cache()
        
        logger.info(
            f"Cargados desde caché: {len(self.investigadores_data)} investigadores, "
            f"{len(DataCache.publicaciones_list)} publicaciones, "
            f"{len(DataCache.proyectos_list)} proyectos, "
            f"{len(self.all_areas)} áreas"
        )

    def _load_from_files(self):
        """Carga datos directamente desde archivos (fallback)."""
        logger.info("📄 Cargando datos desde archivos Excel")
        
        import pandas as pd
        
        academicas_file = os.path.join(self.data_directory, "academicas.xlsx")
        publicaciones_file = os.path.join(self.data_directory, "publicaciones_total.xlsx")
        proyectos_file = os.path.join(self.data_directory, "proyectos_total.xlsx")

        if not os.path.exists(academicas_file):
            logger.error(f"Archivo {academicas_file} no encontrado")
            return

        # Procesar investigadores
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

        publicaciones_data = []
        proyectos_data = []

        if os.path.exists(publicaciones_file):
            df_pub = pd.read_excel(publicaciones_file)
            publicaciones_data = df_pub.to_dict("records")

        if os.path.exists(proyectos_file):
            df_proy = pd.read_excel(proyectos_file)
            proyectos_data = df_proy.to_dict("records")

        self._create_investigators_summary_extended(
            df_academicas, publicaciones_data, proyectos_data
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
            f"{len(publicaciones_data)} publicaciones, "
            f"{len(proyectos_data)} proyectos, "
            f"{len(self.all_areas)} áreas"
        )

    def _create_investigators_summary_from_cache(self):
        """Crea resumen de investigadores usando el DataCache compartido."""
        try:
            area_counts = {}
            investigator_details = []

            # Indexar publicaciones y proyectos por RUT
            pub_by_rut = {}
            proy_by_rut = {}

            for pub in DataCache.publicaciones_list:
                rut = pub.get("rut_ir")
                if rut:
                    if rut not in pub_by_rut:
                        pub_by_rut[rut] = []
                    pub_by_rut[rut].append(pub)

            for proy in DataCache.proyectos_list:
                rut = proy.get("rut_ir")
                if rut:
                    if rut not in proy_by_rut:
                        proy_by_rut[rut] = []
                    proy_by_rut[rut].append(proy)

            # Procesar primeros 30 investigadores
            for inv in self.investigadores_data[:30]:
                areas_str = inv.get("ocde_2", "")
                if areas_str and areas_str != "nan":
                    areas = [a.strip() for a in areas_str.split(",") if a.strip()]
                else:
                    areas = []

                for area in areas:
                    area_counts[area] = area_counts.get(area, 0) + 1

                rut = inv.get("rut_ir")
                publicaciones = pub_by_rut.get(rut, [])
                proyectos = proy_by_rut.get(rut, [])

                pub_titles = [pub.get("titulo", "")[:100] for pub in publicaciones[:3]]
                proy_titles = [proy.get("titulo", "")[:100] for proy in proyectos[:3]]

                inv_detail = f"- {inv.get('name', 'N/A')} (ID: {inv.get('id', 'N/A')}, RUT: {rut}, Áreas: {inv.get('ocde_2', 'N/A')})"
                if pub_titles:
                    inv_detail += f"\n  Publicaciones: {'; '.join(pub_titles)}"
                if proy_titles:
                    inv_detail += f"\n  Proyectos: {'; '.join(proy_titles)}"

                investigator_details.append(inv_detail)

            self.investigadores_summary = f"""
RESUMEN EXTENDIDO DE INVESTIGADORES CON PUBLICACIONES Y PROYECTOS:

ÁREAS OCDE PRINCIPALES:
{", ".join([f"{area} ({count})" for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:15]])}

INVESTIGADORES CON SUS TRABAJOS:
{chr(10).join(investigator_details[:15])}

TOTAL DE INVESTIGADORES: {len(self.investigadores_data)}
TOTAL DE ÁREAS: {len(self.all_areas)}
TOTAL DE PUBLICACIONES: {len(DataCache.publicaciones_list)}
TOTAL DE PROYECTOS: {len(DataCache.proyectos_list)}

INSTRUCCIONES PARA BÚSQUEDA POR TÍTULOS:
- Si el usuario menciona un título de publicación o proyecto específico, busca en los títulos mostrados arriba
- Si encuentras coincidencia parcial en título, devuelve el nombre del investigador asociado
- Ejemplo: "VALIDACION DE ESCALA SOLEDAD" → Alba Zambrano Constanzo
"""

        except Exception as e:
            logger.error(f"Error creando resumen desde caché: {e}")
            self.investigadores_summary = "Error cargando resumen de investigadores"

    def _create_investigators_summary_extended(
        self, df, publicaciones_data: list, proyectos_data: list
    ):
        """Crea un resumen extendido de investigadores (versión archivo)."""
        try:
            area_counts = {}
            investigator_details = []

            pub_by_rut = {}
            proy_by_rut = {}

            for pub in publicaciones_data:
                rut = pub.get("rut_ir")
                if rut:
                    if rut not in pub_by_rut:
                        pub_by_rut[rut] = []
                    pub_by_rut[rut].append(pub)

            for proy in proyectos_data:
                rut = proy.get("rut_ir")
                if rut:
                    if rut not in proy_by_rut:
                        proy_by_rut[rut] = []
                    proy_by_rut[rut].append(proy)

            for _, inv in df.head(30).iterrows():
                areas_str = inv.get("ocde_2", "")
                if areas_str and areas_str != "nan":
                    areas = areas_str.split(",")
                else:
                    areas = []
                areas = [area.strip() for area in areas if area.strip()]

                for area in areas:
                    area_counts[area] = area_counts.get(area, 0) + 1

                rut = inv.get("rut_ir")
                publicaciones = pub_by_rut.get(rut, [])
                proyectos = proy_by_rut.get(rut, [])

                pub_titles = [pub.get("titulo", "")[:100] for pub in publicaciones[:3]]
                proy_titles = [proy.get("titulo", "")[:100] for proy in proyectos[:3]]

                inv_detail = f"- {inv['name']} (ID: {inv['id']}, RUT: {rut}, Áreas: {inv.get('ocde_2', 'N/A')})"
                if pub_titles:
                    inv_detail += f"\n  Publicaciones: {'; '.join(pub_titles)}"
                if proy_titles:
                    inv_detail += f"\n  Proyectos: {'; '.join(proy_titles)}"

                investigator_details.append(inv_detail)

            self.investigadores_summary = f"""
RESUMEN EXTENDIDO DE INVESTIGADORES CON PUBLICACIONES Y PROYECTOS:

ÁREAS OCDE PRINCIPALES:
{", ".join([f"{area} ({count})" for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:15]])}

INVESTIGADORES CON SUS TRABAJOS:
{chr(10).join(investigator_details[:15])}

TOTAL DE INVESTIGADORES: {len(df)}
TOTAL DE ÁREAS: {len(self.all_areas)}
TOTAL DE PUBLICACIONES: {len(publicaciones_data)}
TOTAL DE PROYECTOS: {len(proyectos_data)}

INSTRUCCIONES PARA BÚSQUEDA POR TÍTULOS:
- Si el usuario menciona un título de publicación o proyecto específico, busca en los títulos mostrados arriba
- Si encuentras coincidencia parcial en título, devuelve el nombre del investigador asociado
- Ejemplo: "VALIDACION DE ESCALA SOLEDAD" → Alba Zambrano Constanzo
"""

        except Exception as e:
            logger.error(f"Error creando resumen extendido de investigadores: {e}")
            self.investigadores_summary = "Error cargando resumen extendido de investigadores"

    def _create_agent(self):
        """Crea el agente Agno."""
        try:
            self.agent = Agent(
                model=Claude(id="claude-3-5-haiku-20241022"),
                instructions=f"""Eres un asistente inteligente especializado en búsqueda de investigadoras del Observatorio de Género en Ciencia de la Universidad de La Frontera (UFRO).

INFORMACIÓN DE INVESTIGADORES CON PUBLICACIONES Y PROYECTOS:
{self.investigadores_summary}

ÁREAS OCDE COMPLETAS DISPONIBLES: {", ".join(self.all_areas)}

TU TAREA:
1. Analizar consultas de búsqueda en lenguaje natural sobre investigadoras y sus trabajos
2. DETECTAR AUTOMÁTICAMENTE si la consulta busca:
   - NOMBRES DE PERSONAS (ej: "Alba Zambrano", "María García", "Dr. López")
   - ÁREAS DE INVESTIGACIÓN (ej: "matemáticas", "biotecnología", "psicología")
   - TÍTULOS DE TRABAJOS (ej: "validación escala soledad", "células madre")
   - FILTROS NUMÉRICOS (ej: "más de 20 publicaciones", "al menos 10 proyectos")
   - FILTROS DE ROL (ej: "investigador responsable", "co-investigador", "IR", "co-i")
   - CONSULTAS HÍBRIDAS (combinaciones de lo anterior)
3. Responder SOLO en formato JSON como se especifica abajo

FORMATO DE RESPUESTA REQUERIDO (siempre JSON válido):
{{
    "tipo_busqueda": "nombre|area|titulo|filtro_numerico|rol|hibrida",
    "areas_detectadas": ["área1", "área2"],
    "nombres_detectados": ["nombre1", "nombre2"],
    "titulos_detectados": ["fragmento_titulo1", "fragmento_titulo2"],
    "terminos_busqueda": ["término1", "término2"],
    "min_proyectos": null,
    "min_publicaciones": null,
    "rol_filtro": null,
    "resumen": "breve explicación de los resultados encontrados"
}}

REGLAS PARA DETECCIÓN:
- tipo_busqueda "nombre": Si detectas nombres propios
- tipo_busqueda "area": Si detectas disciplinas/campos
- tipo_busqueda "titulo": Si detectas títulos o fragmentos de publicaciones/proyectos
- tipo_busqueda "filtro_numerico": Si detectas cantidades como "más de X", "al menos X", "mínimo X"
- tipo_busqueda "rol": Si detectas roles como "investigador responsable", "IR", "co-investigador", "co-i"
- tipo_busqueda "hibrida": Si detectas COMBINACIÓN de varios tipos

DETECCIÓN DE FILTROS NUMÉRICOS:
- "más de 20 publicaciones" → min_publicaciones: 20
- "al menos 10 proyectos" → min_proyectos: 10
- "con 15 o más papers" → min_publicaciones: 15
- "mínimo 5 proyectos" → min_proyectos: 5

DETECCIÓN DE ROLES:
- "investigador responsable", "IR", "responsable" → rol_filtro: "ir"
- "co-investigador", "co-i", "coinvestigador" → rol_filtro: "co-i"

EJEMPLOS:
- "investigadoras con más de 20 publicaciones" → tipo_busqueda: "filtro_numerico", min_publicaciones: 20
- "Alba Zambrano" → tipo_busqueda: "nombre", nombres_detectados: ["Alba Zambrano"]
- "biotecnología con más de 5 proyectos" → tipo_busqueda: "hibrida", areas_detectadas: ["BIOTECNOLOGIA..."], min_proyectos: 5
- "investigadoras responsables" → tipo_busqueda: "rol", rol_filtro: "ir"
- "co-investigadoras en matemáticas" → tipo_busqueda: "hibrida", rol_filtro: "co-i", areas_detectadas: ["MATEMATICAS"]""",
                description="Agente de búsqueda inteligente para investigadoras OCDE",
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
        try:
            if not self.agent:
                return self._fallback_search(query)

            if not query.strip():
                return {"error": "Consulta vacía"}

            response = self.agent.run(query)

            if hasattr(response, "content"):
                response_text = str(response.content)
            else:
                response_text = str(response)

            return self._parse_agent_response(response_text)

        except Exception as e:
            logger.error(f"Error en búsqueda inteligente: {e}")
            return self._fallback_search(query)

    def _parse_agent_response(self, response_text: str) -> Dict[str, Any]:
        """Parsea la respuesta JSON del agente."""
        try:
            import json

            start = response_text.find("{")
            end = response_text.rfind("}") + 1

            if start != -1 and end != 0:
                json_str = response_text[start:end]
                data = json.loads(json_str)

                # Validar áreas
                if "areas_detectadas" in data:
                    data["areas_detectadas"] = [
                        area for area in data["areas_detectadas"]
                        if area in self.all_areas
                    ]
                
                # Asegurar que existan todos los campos necesarios
                result = {
                    "tipo_busqueda": data.get("tipo_busqueda", "area"),
                    "areas_detectadas": data.get("areas_detectadas", []),
                    "nombres_detectados": data.get("nombres_detectados", []),
                    "titulos_detectados": data.get("titulos_detectados", []),
                    "terminos_busqueda": data.get("terminos_busqueda", []),
                    "min_proyectos": data.get("min_proyectos"),
                    "min_publicaciones": data.get("min_publicaciones"),
                    "rol_filtro": data.get("rol_filtro"),
                    "resumen": data.get("resumen", ""),
                }
                
                return result

            return self._fallback_search_response(response_text)

        except Exception as e:
            logger.error(f"Error parseando respuesta del agente: {e}")
            return self._fallback_search_response(response_text)

    def _fallback_search(self, query: str) -> Dict[str, Any]:
        """Búsqueda de respaldo cuando el agente no está disponible."""
        try:
            import re
            query_lower = query.lower()

            # Detectar áreas
            detected_areas = []
            for area in self.all_areas:
                if any(word in area.lower() for word in query_lower.split()):
                    detected_areas.append(area)

            search_terms = [word for word in query_lower.split() if len(word) > 2]
            
            # Detectar filtros numéricos
            min_proyectos = None
            min_publicaciones = None
            rol_filtro = None
            
            # Proyectos
            proy_match = re.search(r"(?:más|mas)\s+de\s+(\d+)\s*proyectos?", query_lower)
            if proy_match:
                min_proyectos = int(proy_match.group(1))
            
            # Publicaciones
            pub_match = re.search(r"(?:más|mas)\s+de\s+(\d+)\s*(?:publicaciones?|papers?)", query_lower)
            if pub_match:
                min_publicaciones = int(pub_match.group(1))
            
            # Rol
            if re.search(r"(?:co-?i\b|co-?\s*investigador)", query_lower):
                rol_filtro = "co-i"
            elif re.search(r"(?:\bir\b|responsables?)", query_lower):
                rol_filtro = "ir"
            
            # Determinar tipo de búsqueda
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

    def _fallback_search_response(self, response_text: str) -> Dict[str, Any]:
        """Crear respuesta estructurada cuando el parsing JSON falla."""
        return {
            "tipo_busqueda": "area",
            "areas_detectadas": [],
            "nombres_detectados": [],
            "titulos_detectados": [],
            "terminos_busqueda": [],
            "min_proyectos": None,
            "min_publicaciones": None,
            "rol_filtro": None,
            "resumen": "La búsqueda devolvió resultados pero no en el formato esperado. Intenta reformular tu consulta.",
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
            "model": "Claude Sonnet 4.5 (via Agno)",
            "framework": "Agno (simplified)",
            "uses_shared_cache": USE_SHARED_CACHE,
            "data_directory": self.data_directory,
        }


# Instancia singleton
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
    print("=== AI Search Agent con Agno Framework (Optimizado) ===")
    print("Información del agente:")
    info = get_ai_search_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    if is_ai_search_ready():
        print("\n¡Agente de búsqueda listo!")

        test_queries = [
            "busca investigadoras de matemáticas",
            "encuentra expertas en biotecnología",
            "María García publicaciones sobre células",
        ]

        for query in test_queries:
            print(f"\nConsulta: {query}")
            result = get_ai_search_response(query)
            print(f"Áreas detectadas: {result.get('areas_detectadas', [])}")
            print(f"Términos de búsqueda: {result.get('terminos_busqueda', [])}")
            print(f"Resumen: {result.get('resumen', 'Sin resumen')[:100]}...")
    else:
        print("\nAgente de búsqueda no está listo. Verifica la configuración.")