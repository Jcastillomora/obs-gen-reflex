# backend.py - Versión optimizada con caché compartido
"""
Backend optimizado que usa DataCache compartido.
Compatible 100% con OCDE.py - no requiere cambios en las páginas.

UBICACIÓN: OCDE/backend/backend.py
"""

import reflex as rx
import asyncio
import logging
import re
import unicodedata
from .data_items import all_items
from .data_cache import DataCache  # Caché compartido
from .models import Investigador, Publicaciones, Proyectos, Documento
from typing import Dict, List, Optional
from sqlmodel import select

logger = logging.getLogger(__name__)

# Carousel
CAROUSEL_SLEEP_SECONDS = 8

# Patrones regex para detección de filtros numéricos en AI Search
_PROYECTO_PATTERNS = [
    r"(?:más|mas|mayor|mayores)\s*(?:de|que)\s*(\d+)\s*(?:proyectos?|projects?)",
    r"(\d+)\s*(?:o\s*)?(?:más|mas)\s*proyectos?",
    r"(?:al\s*menos|mínimo|minimo|min)\s*(\d+)\s*proyectos?",
    r"(?:con|tengan?|tienen?)\s*(?:más|mas)?\s*(?:de)?\s*(\d+)\s*proyectos?",
    r">\s*(\d+)\s*proyectos?",
    r">=\s*(\d+)\s*proyectos?",
]

_PUB_PATTERNS = [
    r"(?:más|mas|mayor|mayores)\s*(?:de|que)\s*(\d+)\s*(?:publicacion|publicaciones|publications?|papers?|artículos?|articulos?)",
    r"(\d+)\s*(?:o\s*)?(?:más|mas)\s*(?:publicacion|publicaciones|papers?)",
    r"(?:al\s*menos|mínimo|minimo|min)\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
    r"(?:con|tengan?|tienen?)\s*(?:más|mas)?\s*(?:de)?\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
    r">\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
    r">=\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
]

_ROL_CO_PATTERN = r"(?:co-?i\b|co-?\s*investigador[aes]?|coinvestigador[aes]?)"
_ROL_IR_PATTERN = r"(?:\bir\b|investigador[aes]?\s+responsables?|responsables?|principales?)"

# Palabras genéricas que NO aportan al significado temático de la búsqueda
_BROAD_SEARCH_STOPWORDS = {
    "investigadoras", "investigadora", "investigadores", "investigador",
    "expertas", "experta", "expertos", "experto",
    "mujeres", "mujer", "chile", "ufro", "universidad",
    "busca", "busco", "necesito", "quiero", "dame", "dime",
    "encuentra", "encontrar", "mostrar", "muestra", "listar",
    "docentes", "profesoras", "profesora", "academicas", "academica",
    "cientificas", "cientifica", "cientificos", "cientifico",
    "todas", "todos", "lista", "dame", "tengan", "tienen",
}


class State(rx.State):
    """The app state."""

    image_urls: list[dict[str, str]] = [
        {
            "src": "https://generoenciencia.ufro.cl/wp-content/uploads/2025/09/banner-adj-redes-mujeres-ciencia.webp",
            "link": "https://vrip.ufro.cl/investigacion-2/investigadoras-ufro-lideraran-proyectos-para-fortalecer-la-cooperacion-cientifica-y-abrir-nuevas-oportunidades-para-mujeres-en-ciencia",
        },
        {
            "src": "https://generoenciencia.ufro.cl/wp-content/uploads/2025/09/banner-ecocrearte.webp",
            "link": "https://generoenciencia.ufro.cl/2025/09/08/investigadoras-ufro-impulsan-iniciativa-para-promover-la-reinsercion-sociolaboral-de-mujeres-privadas-de-libertad-en-la-araucania",
        },
        {
            "src": "https://generoenciencia.ufro.cl/wp-content/uploads/2025/08/banner-taller-branding.webp",
            "link": "https://vrip.ufro.cl/investigacion-2/academicas-ufro-fortalecen-liderazgo-y-comunicacion-cientifica-en-jornada-organizada-por-ines-de-genero",
        },
        {
            "src": "https://generoenciencia.ufro.cl/wp-content/uploads/2025/08/banner-encuentro-academicas.webp",
            "link": "https://vrip.ufro.cl/investigacion-2/mujeres-lideres-en-ciencia-innovacion-y-emprendimiento-protagonizaran-el-encuentro-red-de-academicas-ufro/",
        },
    ]
    current_index: int = 0

    proyectos: list[Proyectos] = []
    investigadores: list[Investigador] = []
    publicaciones: list[Publicaciones] = []
    grid_data: list[dict] = []
    grid_data2: list[dict] = []

    search_value: str = ""
    search_value_pub: str = ""
    search_value_proy: str = ""
    search_value_card: str = ""
    sort_value: str = ""
    sort_reverse: bool = False
    search_term: str = ""
    filtered_count: int = 0
    filtered_year: list = []
    filtered_count_pub: int = 0

    min_proyectos: str = ""
    min_publicaciones: str = ""
    search_rol: str = ""

    total_items: int = 0
    total_items_pub: int = 0  # Para publicaciones
    total_investigadores: int = 0
    offset: int = 0
    offset_pub: int = 0  # Para publicaciones
    limit: int = 24

    name: str = ""
    institucion: str = ""
    email: str = ""
    city: str = ""
    message: str = ""

    selected_items: Dict[str, List] = all_items

    all_areas: list[str] = []
    selected_areas: list[str] = []
    selected_area: str = ""
    selected_area_temp: str = ""

    # Chatbot
    chatbot_messages: List[Dict[str, str]] = []
    chatbot_input: str = ""
    chatbot_status: str = "not_initialized"
    chatbot_session_id: Optional[str] = None
    chatbot_is_loading: bool = False
    chatbot_error: str = ""

    # AI Search
    ai_search_input: str = ""
    ai_search_query: str = ""
    ai_search_loading: bool = False
    ai_search_error: str = ""
    ai_search_results_summary: str = ""
    ai_detected_areas: list[str] = []
    ai_search_ruts: list[str] = []

    # Repositorio (cargado de DB)
    reportes_items: list[dict] = []
    documentos_items: list[dict] = []

    # =========================================================
    # CAROUSEL
    # =========================================================
    
    @rx.event
    def next_image(self):
        self.current_index = (self.current_index + 1) % len(self.image_urls)

    @rx.event
    def prev_image(self):
        self.current_index = (self.current_index - 1 + len(self.image_urls)) % len(self.image_urls)

    @rx.event(background=True)
    async def start_autoscroll(self):
        while True:
            await asyncio.sleep(CAROUSEL_SLEEP_SECONDS)
            async with self:
                self.current_index = (self.current_index + 1) % len(self.image_urls)

    # =========================================================
    # ÁREAS
    # =========================================================
    
    @rx.event
    def add_area(self, area: str):
        if area not in self.selected_areas:
            self.selected_areas.append(area)

    @rx.event
    def remove_area(self, area: str):
        if area in self.selected_areas:
            self.selected_areas.remove(area)

    @rx.event
    def select_all_areas(self):
        self.selected_areas = list(self.all_areas)

    @rx.event
    def clear_areas(self):
        self.selected_areas.clear()

    @rx.var
    def year_list(self) -> list:
        return self.filtered_year

    # =========================================================
    # FILTROS OPTIMIZADOS - Usando DataCache
    # =========================================================
    
    @rx.var
    def filtered_investigators(self) -> list[Investigador]:
        """Filtrado optimizado usando índices pre-calculados.

        Dos caminos mutuamente excluyentes:
        - ai_search_ruts activo → búsqueda semántica amplia (grado, pub, proyectos)
        - Sin ai_search_ruts   → filtrado clásico por texto/áreas OCDE
        En ambos casos se aplican los filtros numéricos y de rol al final.
        """
        # --- CAMINO 1: Búsqueda semántica amplia (RUTs del backend search) ---
        if self.ai_search_ruts:
            ruts_set = set(self.ai_search_ruts)
            filtered = [inv for inv in self.investigadores if inv.rut_ir in ruts_set]

        # --- CAMINO 2: Filtrado clásico por texto y áreas OCDE ---
        else:
            term = self.search_term.lower().strip()
            if term:
                filtered = [
                    inv for inv in self.investigadores
                    if (term in str(inv.id))
                    or (term in (inv.nombre + " " + inv.apellido1 + " " + inv.apellido2).lower())
                    or (term in inv.ocde_2.lower())
                ]
            else:
                filtered = self.investigadores

            if self.selected_areas:
                filtered = [
                    inv for inv in filtered
                    if any(area in inv.ocde_2 for area in self.selected_areas)
                ]

        # --- FILTROS NUMÉRICOS Y DE ROL (aplican a ambos caminos) ---
        if self.min_proyectos.strip() and self.min_proyectos.strip().isdigit():
            min_proy = int(self.min_proyectos.strip())
            filtered = [
                inv for inv in filtered
                if DataCache.get_proyectos_count(inv.rut_ir) >= min_proy
            ]

        if self.min_publicaciones.strip() and self.min_publicaciones.strip().isdigit():
            min_pub = int(self.min_publicaciones.strip())
            filtered = [
                inv for inv in filtered
                if DataCache.get_publicaciones_count(inv.rut_ir) >= min_pub
            ]

        if self.search_rol.strip():
            filtered = [
                inv for inv in filtered
                if DataCache.has_rol(inv.rut_ir, self.search_rol.strip())
            ]

        return filtered

    # Compatibilidad con código existente
    def get_investigator_counts(self, investigador: Investigador) -> dict:
        return {
            "proyectos": DataCache.get_proyectos_count(investigador.rut_ir),
            "publicaciones": DataCache.get_publicaciones_count(investigador.rut_ir)
        }

    def investigator_has_rol(self, investigador: Investigador, search_rol: str) -> bool:
        return DataCache.has_rol(investigador.rut_ir, search_rol)

    @rx.var
    def sorted_areas(self) -> list[str]:
        return sorted([a for a in self.all_areas if a.strip()])

    @rx.var
    def sorted_selected_areas(self) -> list[str]:
        return sorted(self.selected_areas)

    @rx.event
    def add_selected_area(self):
        if self.selected_area_temp and self.selected_area_temp not in self.selected_areas:
            self.selected_areas.append(self.selected_area_temp)

    @rx.var
    def current_investigator_fullname(self) -> str:
        if self.current_investigator_is_none:
            return ""
        inv = self.current_investigator
        return (inv.nombre + " " + inv.apellido1 + " " + inv.apellido2).strip()

    @rx.var
    def get_initials(self) -> str:
        if self.current_investigator_is_none or not self.current_investigator.nombre:
            return "??"
        nombre   = self.current_investigator.nombre
        apellido = self.current_investigator.apellido1
        if apellido:
            return (nombre[0] + apellido[0]).upper()
        return nombre[0].upper()

    # =========================================================
    # MÉTODOS DE CARGA - REQUERIDOS POR OCDE.py
    # =========================================================

    @rx.event
    def load_grid_data(self):
        """Carga datos del grid usando DataCache."""
        if self.current_investigator:
            rut = str(self.current_investigator.rut_ir)
            
            df_proy = DataCache.get_proyectos_by_rut(rut)
            df_pub = DataCache.get_publicaciones_by_rut(rut)
            
            self.grid_data = df_proy.to_dict("records") if not df_proy.empty else []
            self.grid_data2 = df_pub.to_dict("records") if not df_pub.empty else []
            self.filtered_count = len(df_proy)
            self.filtered_year = df_proy["año"].tolist() if not df_proy.empty else []
            self.filtered_count_pub = len(df_pub)

    def set_search_term(self, term: str):
        self.search_term = term

    @rx.event
    def set_min_proyectos(self, value: str):
        if value.strip() == "":
            self.min_proyectos = ""
        elif value.strip().isdigit() and int(value.strip()) >= 0:
            self.min_proyectos = value.strip()

    @rx.event
    def set_min_publicaciones(self, value: str):
        if value.strip() == "":
            self.min_publicaciones = ""
        elif value.strip().isdigit() and int(value.strip()) >= 0:
            self.min_publicaciones = value.strip()

    @rx.event
    def set_search_rol(self, value: str):
        self.search_rol = value.strip()

    @rx.var
    def search_results_empty(self) -> bool:
        return len(self.filtered_investigators) == 0

    @rx.var
    def search_message(self) -> str:
        total = len(self.filtered_investigators)
        if total == 0:
            if (self.search_term.strip() or self.min_proyectos.strip() or 
                self.min_publicaciones.strip() or self.search_rol.strip() or 
                self.selected_areas):
                return "No se encontraron investigadoras que coincidan con los filtros aplicados."
            return "No hay datos disponibles."
        return f"Se encontraron {total} investigadoras."

    @rx.var
    def current_investigator(self) -> Optional[Investigador]:
        if not self.id:
            return None
        try:
            search_id = int(self.id)
        except ValueError:
            return None
        for inv in self.investigadores:
            if inv.id == search_id:
                return inv
        return None

    @rx.var
    def current_investigator_is_none(self) -> bool:
        return self.current_investigator is None

    # =========================================================
    # load_academicas - Requerido por OCDE.py línea 225
    # =========================================================
    
    @rx.event
    def load_academicas(self):
        """Carga lista de investigadoras usando DataCache compartido."""
        # Inicializar caché si no está listo
        if not DataCache.is_initialized():
            DataCache.initialize()
        
        # Usar datos del caché
        self.investigadores = [
            Investigador(**row) 
            for row in DataCache.investigadores_list
        ]
        
        self.total_investigadores = len(self.investigadores)
        self.all_areas = list(DataCache.all_areas)

    # =========================================================
    # load_entries - Requerido por OCDE.py línea 358
    # =========================================================
    
    @rx.event
    def load_entries(self):
        """Carga proyectos del investigador actual usando DataCache."""
        if self.current_investigator is None:
            logger.error("load_entries: current_investigator es None.")
            return

        rut = str(self.current_investigator.rut_ir)
        df = DataCache.get_proyectos_by_rut(rut)
        
        if df.empty:
            self.proyectos = []
            self.total_items = 0
            return
        
        self.proyectos = [Proyectos(**row) for _, row in df.iterrows()]
        self.total_items = len(self.proyectos)
        self.offset = 0  # Resetear paginación al cargar nuevos proyectos

    # =========================================================
    # load_entries_pub - Requerido por OCDE.py línea 358
    # =========================================================
    
    @rx.event
    def load_entries_pub(self):
        """Carga publicaciones del investigador actual usando DataCache."""
        if self.current_investigator is None:
            logger.error("load_entries_pub: current_investigator es None.")
            return

        rut = str(self.current_investigator.rut_ir)
        df = DataCache.get_publicaciones_by_rut(rut)
        
        if df.empty:
            self.publicaciones = []
            self.total_items_pub = 0
            return
        
        self.publicaciones = [Publicaciones(**row) for _, row in df.iterrows()]
        self.total_items_pub = len(self.publicaciones)
        self.offset_pub = 0  # Resetear paginación al cargar nuevas publicaciones

    # =========================================================
    # PROYECTOS Y PUBLICACIONES - FILTROS
    # =========================================================
    
    @rx.var
    def total_proyectos(self) -> int:
        return len(self.proyectos)

    @rx.var
    def filtered_sorted_proyectos(self) -> list[Proyectos]:
        proyectos = self.proyectos
        if self.search_value_proy:
            search_value = self.search_value_proy.lower()
            proyectos = [
                proyecto for proyecto in proyectos
                if any(
                    search_value in str(getattr(proyecto, attr)).lower()
                    for attr in ["codigo", "titulo", "año", "ocde_2", "tipo_proyecto", 
                                "investigador_responsable", "rol"]
                )
            ]
        return proyectos

    @rx.var
    def filtered_sorted_pub(self) -> list[Publicaciones]:
        publicaciones = self.publicaciones
        if self.search_value_pub:
            search_value = self.search_value_pub.lower()
            publicaciones = [
                publicacion for publicacion in publicaciones
                if any(
                    search_value in str(getattr(publicacion, attr)).lower()
                    for attr in ["año", "titulo", "revista", "cuartil", "autor", 
                                "wos_id", "liderado", "url"]
                )
            ]
        return publicaciones

    # =========================================================
    # PAGINACIÓN - PROYECTOS
    # =========================================================
    
    @rx.var
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.var
    def total_pages(self) -> int:
        if self.total_items == 0:
            return 1  # Al menos 1 página aunque esté vacía
        return (self.total_items // self.limit) + (1 if self.total_items % self.limit else 0)

    @rx.var(initial_value=[])
    def get_current_page(self) -> list[Proyectos]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_proyectos[start_index:end_index]

    @rx.event
    def prev_page(self):
        if self.page_number > 1:
            self.offset -= self.limit

    @rx.event
    def next_page(self):
        if self.page_number < self.total_pages:
            self.offset += self.limit

    @rx.event
    def first_page(self):
        self.offset = 0

    @rx.event
    def last_page(self):
        if self.total_pages > 0:
            self.offset = (self.total_pages - 1) * self.limit

    # =========================================================
    # PAGINACIÓN - PUBLICACIONES
    # =========================================================
    
    @rx.var
    def page_number_pub(self) -> int:
        return (self.offset_pub // self.limit) + 1

    @rx.var
    def total_pages_pub(self) -> int:
        if self.total_items_pub == 0:
            return 1  # Al menos 1 página aunque esté vacía
        return (self.total_items_pub // self.limit) + (1 if self.total_items_pub % self.limit else 0)

    @rx.var(initial_value=[])
    def get_current_page_pub(self) -> list[Publicaciones]:
        start_index = self.offset_pub
        end_index = start_index + self.limit
        return self.filtered_sorted_pub[start_index:end_index]

    @rx.event
    def prev_page_pub(self):
        if self.page_number_pub > 1:
            self.offset_pub -= self.limit

    @rx.event
    def next_page_pub(self):
        if self.page_number_pub < self.total_pages_pub:
            self.offset_pub += self.limit

    @rx.event
    def first_page_pub(self):
        self.offset_pub = 0

    @rx.event
    def last_page_pub(self):
        if self.total_pages_pub > 0:
            self.offset_pub = (self.total_pages_pub - 1) * self.limit

    @rx.event
    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()

    # =========================================================
    # SELECTED ITEMS
    # =========================================================
    
    def add_selected(self, list_name: str, item: str):
        self.selected_items[list_name].append(item)

    def remove_selected(self, list_name: str, item: str):
        self.selected_items[list_name].remove(item)

    def add_all_selected(self, list_name: str):
        self.selected_items[list_name] = list(all_items[list_name])

    def clear_selected(self, list_name: str):
        self.selected_items[list_name].clear()

    # =========================================================
    # CHATBOT
    # =========================================================
    
    @rx.event(background=True)
    async def initialize_chatbot(self):
        async with self:
            try:
                self.chatbot_status = "initializing"
                self.chatbot_error = ""

                from .chatbot.pdf_agent import is_pdf_chatbot_ready, get_pdf_chatbot_info

                if is_pdf_chatbot_ready():
                    self.chatbot_status = "ready"
                    self.chatbot_messages = [
                        {
                            "role": "assistant",
                            "content": "¡Hola! Soy tu asistente para consultas sobre reportes y documentos del Observatorio. ¿En qué puedo ayudarte?",
                        }
                    ]
                else:
                    self.chatbot_status = "error"
                    info = get_pdf_chatbot_info()
                    if not info.get("ready", False):
                        self.chatbot_error = "No se pudo inicializar el chatbot."

            except Exception as e:
                self.chatbot_status = "error"
                self.chatbot_error = f"Error al inicializar: {str(e)}"

    @rx.event
    def set_chatbot_input(self, value: str):
        self.chatbot_input = value

    @rx.event
    def handle_chatbot_key_press(self, key: str):
        if key == "Enter" and not self.chatbot_is_loading and self.chatbot_input.strip():
            return type(self).send_user_message_immediate

    @rx.event
    def send_user_message_immediate(self):
        if not self.chatbot_input.strip() or self.chatbot_is_loading:
            return

        user_message = {"role": "user", "content": self.chatbot_input.strip()}
        self.chatbot_messages.append(user_message)

        user_input = self.chatbot_input.strip()
        self.chatbot_input = ""
        self.chatbot_is_loading = True
        self.chatbot_error = ""

        return State.process_ai_response(user_input)

    @rx.event(background=True)
    async def process_ai_response(self, user_input: str):
        try:
            from .chatbot.pdf_agent import get_pdf_chatbot_response
            response = await asyncio.to_thread(get_pdf_chatbot_response, user_input)

            async with self:
                assistant_message = {"role": "assistant", "content": response}
                self.chatbot_messages.append(assistant_message)

        except Exception as e:
            async with self:
                self.chatbot_error = f"Error: {str(e)}"
                if self.chatbot_messages and self.chatbot_messages[-1]["role"] == "user":
                    self.chatbot_messages.pop()
        finally:
            async with self:
                self.chatbot_is_loading = False

    # =========================================================
    # AI SEARCH
    # =========================================================
    
    @rx.event
    def set_ai_search_input(self, value: str):
        self.ai_search_input = value

    @rx.event
    def set_ai_search_query(self, query: str):
        self.ai_search_input = query

    @rx.event
    def handle_ai_search_enter(self, key: str):
        if key == "Enter":
            return type(self).perform_ai_search

    @rx.event(background=True)
    async def perform_ai_search(self):
        async with self:
            search_text = self.ai_search_input.strip()
            if not search_text:
                self.search_term = ""
                self.selected_areas = []
                self.ai_detected_areas = []
                self.ai_search_ruts = []
                self.min_proyectos = ""
                self.min_publicaciones = ""
                self.search_rol = ""
                self.ai_search_results_summary = f"Mostrando todas las investigadoras ({len(self.investigadores)})"
                self.ai_search_error = ""
                return

            self.ai_search_query = search_text
            self.ai_search_loading = True
            self.ai_search_error = ""
            self.ai_search_results_summary = ""
            # Limpiar búsqueda normal para evitar interferencias
            self.search_term = ""
            self.selected_areas = []

        try:
            from .chatbot.ai_search_agent import get_ai_search_response, is_ai_search_ready

            if not is_ai_search_ready():
                await asyncio.sleep(0.5)
                async with self:
                    self._perform_simple_ai_search()
            else:
                await asyncio.sleep(0.5)
                response = await asyncio.get_event_loop().run_in_executor(
                    None, get_ai_search_response, self.ai_search_query
                )
                async with self:
                    self._process_ai_search_response(response)

        except Exception as e:
            async with self:
                self.ai_search_error = f"Error en búsqueda con IA: {str(e)}"
                self._perform_simple_ai_search()
        finally:
            async with self:
                self.ai_search_loading = False

    def _perform_simple_ai_search(self):
        """Fallback de búsqueda simple con detección robusta de filtros."""
        query = self.ai_search_query.lower()
        logger.debug("AI Search simple query: '%s'", query)

        detected_areas = []
        applied_filters = []

        # Buscar proyectos
        proyecto_match = None
        for pattern in _PROYECTO_PATTERNS:
            proyecto_match = re.search(pattern, query)
            if proyecto_match:
                break

        # Buscar publicaciones
        pub_match = None
        for pattern in _PUB_PATTERNS:
            pub_match = re.search(pattern, query)
            if pub_match:
                break

        rol_co_match = re.search(_ROL_CO_PATTERN, query)
        rol_ir_match = re.search(_ROL_IR_PATTERN, query)

        if proyecto_match:
            self.min_proyectos = str(int(proyecto_match.group(1)))
            applied_filters.append(f"mínimo {self.min_proyectos} proyectos")
        else:
            self.min_proyectos = ""

        if pub_match:
            self.min_publicaciones = str(int(pub_match.group(1)))
            applied_filters.append(f"mínimo {self.min_publicaciones} publicaciones")
        else:
            self.min_publicaciones = ""

        if rol_co_match:
            self.search_rol = "co-i"
            applied_filters.append("rol co-investigador")
        elif rol_ir_match:
            self.search_rol = "ir"
            applied_filters.append("rol investigador responsable")
        else:
            self.search_rol = ""

        for area in self.all_areas:
            if any(word in area.lower() for word in query.split()):
                detected_areas.append(area)

        has_numeric_filter = proyecto_match or pub_match or rol_co_match or rol_ir_match
        if not has_numeric_filter:
            self.ai_detected_areas = detected_areas[:3]
            self.selected_areas = detected_areas[:3]
            # Si no hay áreas exactas, activar búsqueda semántica amplia
            if not detected_areas:
                self.ai_search_ruts = self._find_ruts_by_broad_search(self.ai_search_query)
                self.search_term = ""
            else:
                self.ai_search_ruts = []
                self.search_term = self.ai_search_query
        else:
            self.ai_detected_areas = []
            self.selected_areas = []
            self.ai_search_ruts = []
            self.search_term = ""

        if applied_filters:
            self.ai_search_results_summary = f"Filtros aplicados: {', '.join(applied_filters)}"
        else:
            self.ai_search_results_summary = f"Búsqueda por '{self.ai_search_query}'"

        logger.debug("AI Search resumen: %s", self.ai_search_results_summary)

    def _process_ai_search_response(self, response):
        """Procesa respuesta de IA."""
        try:
            # =====================================================
            # PASO 1: SIEMPRE detectar filtros numéricos primero
            # Esto funciona independiente de la respuesta del agente
            # =====================================================
            query = self.ai_search_query.lower()
            applied_filters = []

            logger.debug("Procesando AI Search response para query: '%s'", query)

            min_proy_detected = None
            for pattern in _PROYECTO_PATTERNS:
                match = re.search(pattern, query)
                if match:
                    min_proy_detected = int(match.group(1))
                    break

            min_pub_detected = None
            for pattern in _PUB_PATTERNS:
                match = re.search(pattern, query)
                if match:
                    min_pub_detected = int(match.group(1))
                    break

            rol_detected = None
            if re.search(_ROL_CO_PATTERN, query):
                rol_detected = "co-i"
            elif re.search(_ROL_IR_PATTERN, query):
                rol_detected = "ir"
            
            # =====================================================
            # PASO 2: Procesar respuesta del agente
            # =====================================================
            if isinstance(response, dict):
                data = response
            else:
                import json
                response_str = str(response)
                start = response_str.find("{")
                end = response_str.rfind("}") + 1
                if start != -1 and end != 0:
                    data = json.loads(response_str[start:end])
                else:
                    data = {}

            tipo_busqueda = data.get("tipo_busqueda", "area")
            detected_areas = data.get("areas_detectadas", [])
            detected_names = data.get("nombres_detectados", [])
            search_terms = data.get("terminos_busqueda", [])
            summary = data.get("resumen", "")

            # Usar filtros del agente si no se detectaron por regex
            agent_min_proy = data.get("min_proyectos")
            agent_min_pub = data.get("min_publicaciones")
            agent_rol = data.get("rol_filtro")

            valid_areas = [area for area in detected_areas if area in self.all_areas]

            # =====================================================
            # PASO 3: Aplicar filtros (prioridad: regex > agente)
            # =====================================================
            
            # Proyectos
            if min_proy_detected is not None:
                self.min_proyectos = str(min_proy_detected)
                applied_filters.append(f"≥{min_proy_detected} proyectos")
            elif agent_min_proy is not None:
                self.min_proyectos = str(agent_min_proy)
                applied_filters.append(f"≥{agent_min_proy} proyectos")
            else:
                self.min_proyectos = ""
            
            # Publicaciones
            if min_pub_detected is not None:
                self.min_publicaciones = str(min_pub_detected)
                applied_filters.append(f"≥{min_pub_detected} publicaciones")
            elif agent_min_pub is not None:
                self.min_publicaciones = str(agent_min_pub)
                applied_filters.append(f"≥{agent_min_pub} publicaciones")
            else:
                self.min_publicaciones = ""
            
            # Rol
            if rol_detected:
                self.search_rol = rol_detected
                applied_filters.append(f"rol: {rol_detected}")
            elif agent_rol:
                self.search_rol = agent_rol
                applied_filters.append(f"rol: {agent_rol}")
            else:
                self.search_rol = ""
            
            logger.debug("Filtros aplicados: %s", applied_filters)

            # =====================================================
            # PASO 4: Aplicar filtros de nombre/área
            # =====================================================
            
            # Solo aplicar filtros de nombre/área si NO hay filtros numéricos
            if not applied_filters:
                if tipo_busqueda == "nombre" and detected_names:
                    self.search_term = " ".join(detected_names)
                    self.selected_areas = []
                elif tipo_busqueda == "area" and valid_areas:
                    self.selected_areas = valid_areas
                    self.search_term = ""
                else:
                    self.selected_areas = valid_areas
                    self.search_term = " ".join(search_terms) if search_terms else ""
            else:
                # Con filtros numéricos, limpiar otros filtros para enfocarse
                self.search_term = ""
                self.selected_areas = []

            self.ai_detected_areas = valid_areas

            # Búsqueda semántica amplia: activar cuando no hay áreas OCDE exactas
            # y la búsqueda NO es estrictamente de filtro numérico o rol puro
            if not valid_areas and tipo_busqueda not in ("filtro_numerico", "rol"):
                # Preferir los términos limpios del LLM; si vienen vacíos usar la query completa
                broad_input = " ".join(search_terms) if search_terms else self.ai_search_query
                self.ai_search_ruts = self._find_ruts_by_broad_search(broad_input)
                if self.ai_search_ruts:
                    # No llenar el buscador normal cuando la búsqueda amplia está activa
                    self.search_term = ""
            else:
                self.ai_search_ruts = []

            # Construir resumen basado en resultados reales (no en el texto del LLM)
            if applied_filters:
                self.ai_search_results_summary = f"Filtros aplicados: {', '.join(applied_filters)}"
            elif self.ai_search_ruts:
                count = len(self.ai_search_ruts)
                term_display = " ".join(search_terms) if search_terms else self.ai_search_query
                plural = "s" if count != 1 else ""
                self.ai_search_results_summary = (
                    f"{count} investigadora{plural} encontrada{plural} relacionada{plural} con '{term_display}'"
                )
            elif valid_areas:
                self.ai_search_results_summary = f"Búsqueda por área: {', '.join(valid_areas)}"
            else:
                self.ai_search_results_summary = f"Búsqueda por '{self.ai_search_query}'"

        except Exception as e:
            logger.error("Error en _process_ai_search_response: %s", e)
            self.ai_search_error = f"Error procesando respuesta: {str(e)}"
            self._perform_simple_ai_search()

    @staticmethod
    def _normalize(text: str) -> str:
        """Elimina acentos y pasa a minúsculas para comparación insensible a acentos."""
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()

    def _find_ruts_by_broad_search(self, query: str) -> list:
        """
        Búsqueda amplia en DataCache: ocde_2, grado_mayor, títulos de publicaciones y proyectos.
        Filtra stopwords genéricos y normaliza acentos.
        Retorna RUTs ordenados por relevancia (más coincidencias primero).
        """
        norm_query = self._normalize(query)
        # Solo palabras temáticamente significativas (>3 chars, no stopwords)
        words = [
            w for w in norm_query.split()
            if len(w) > 3 and w not in _BROAD_SEARCH_STOPWORDS
        ]
        if not words:
            return []

        rut_scores: dict = {}

        # Búsqueda en ocde_2 y grado_mayor (campos de perfil académico)
        for inv in DataCache.investigadores_list:
            rut = inv.get("rut_ir", "")
            ocde = self._normalize(str(inv.get("ocde_2", "")))
            grado = self._normalize(str(inv.get("grado_mayor", "")))
            for word in words:
                if word in ocde:
                    rut_scores[rut] = rut_scores.get(rut, 0) + 3
                if word in grado:
                    rut_scores[rut] = rut_scores.get(rut, 0) + 3

        # Búsqueda en títulos de publicaciones (peso 1)
        for pub in DataCache.publicaciones_list:
            rut = pub.get("rut_ir", "")
            titulo = self._normalize(str(pub.get("titulo", "")))
            for word in words:
                if word in titulo:
                    rut_scores[rut] = rut_scores.get(rut, 0) + 1

        # Búsqueda en títulos de proyectos (peso 1)
        for proy in DataCache.proyectos_list:
            rut = proy.get("rut_ir", "")
            titulo = self._normalize(str(proy.get("titulo", "")))
            for word in words:
                if word in titulo:
                    rut_scores[rut] = rut_scores.get(rut, 0) + 1

        if not rut_scores:
            return []

        sorted_ruts = sorted(rut_scores.items(), key=lambda x: x[1], reverse=True)

        # Si hay investigadoras con coincidencia en perfil académico (score >= 3),
        # excluir las que solo aparecen tangencialmente en publicaciones/proyectos (score < 3).
        # Esto evita que aparezca alguien que tiene 1 paper con el tema pero no es experta.
        profile_matches = [rut for rut, score in sorted_ruts if score >= 3]
        if profile_matches:
            return profile_matches
        # Fallback: si nadie tiene coincidencia en perfil, retornar todos (tema muy específico)
        return [rut for rut, _ in sorted_ruts]

    @rx.event
    def clear_ai_search(self):
        """Limpia toda la búsqueda con IA y restaura el estado inicial."""
        self.ai_search_input = ""
        self.ai_search_query = ""
        self.ai_search_loading = False
        self.ai_search_error = ""
        self.ai_search_results_summary = ""
        self.ai_detected_areas = []
        self.ai_search_ruts = []
        self.search_term = ""
        self.selected_areas = []
        self.min_proyectos = ""
        self.min_publicaciones = ""
        self.search_rol = ""

    @rx.event
    def clear_ai_detected_areas(self):
        self.ai_detected_areas = []
        self.ai_search_ruts = []

    # =========================================================
    # REPOSITORIO (DB)
    # =========================================================

    @rx.event
    def load_repositorio(self):
        _DEFAULTS = [
            {
                "titulo": "Brechas de Género en Educación Superior 2025",
                "descripcion": "Servicio de Información de Educación Superior, 2026",
                "tipo": "documento",
                "filename": "Informe-de-Brechas-en-Educacion-Superior-2025-marzo-2026.pdf",
                "created_at": "2026-03-01",
            },
            {
                "titulo": "Alianza de mujeres en la academia",
                "descripcion": "Universidad de los Andes, 2024",
                "tipo": "documento",
                "filename": "alianza_mujeres.pdf",
                "created_at": "2024-01-01",
            },
            {
                "titulo": "Encuesta mujeres en la academia (EMA)",
                "descripcion": "Universidad Mayor, 2025",
                "tipo": "documento",
                "filename": "encuesta_EMA.pdf",
                "created_at": "2025-01-01",
            },
        ]
        try:
            with rx.session() as session:
                # Sembrar datos iniciales si la tabla está vacía
                count = len(session.exec(select(Documento)).all())
                if count == 0:
                    for d in _DEFAULTS:
                        session.add(Documento(**d))
                    session.commit()

                reportes = session.exec(
                    select(Documento).where(Documento.tipo == "reporte")
                ).all()
                self.reportes_items = [
                    {
                        "heading_text": doc.titulo,
                        "body_text": doc.descripcion,
                        "download_url": f"/{doc.filename}",
                    }
                    for doc in reportes
                ]
                documentos = session.exec(
                    select(Documento).where(Documento.tipo == "documento")
                ).all()
                self.documentos_items = [
                    {
                        "heading_text": doc.titulo,
                        "body_text": doc.descripcion,
                        "download_url": f"/{doc.filename}",
                    }
                    for doc in documentos
                ]
        except Exception as e:
            logger.error("Error cargando repositorio: %s", e)
            self.reportes_items = []
            self.documentos_items = []
        self.ai_search_results_summary = ""