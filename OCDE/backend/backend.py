# backend.py - Versión optimizada con caché compartido
"""
Backend optimizado que usa DataCache compartido.
Compatible 100% con OCDE.py - no requiere cambios en las páginas.

UBICACIÓN: OCDE/backend/backend.py
"""

import reflex as rx
import asyncio
from .data_items import all_items
from .data_cache import DataCache  # Caché compartido
import pandas as pd
import numpy as np
from .models import Investigador, Publicaciones, Proyectos
from typing import Dict, List, Optional


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
            await asyncio.sleep(8)
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
        """Filtrado optimizado usando índices pre-calculados."""
        term = self.search_term.lower().strip()

        if term:
            filtered = [
                inv for inv in self.investigadores
                if (term in str(inv.id))
                or (term in inv.name.lower())
                or (term in inv.ocde_2.lower())
            ]
        else:
            filtered = self.investigadores

        if self.selected_areas:
            filtered = [
                inv for inv in filtered
                if any(area in inv.ocde_2 for area in self.selected_areas)
            ]

        # Filtro por proyectos - O(1) usando DataCache
        if self.min_proyectos.strip() and self.min_proyectos.strip().isdigit():
            min_proy = int(self.min_proyectos.strip())
            filtered = [
                inv for inv in filtered
                if DataCache.get_proyectos_count(inv.rut_ir) >= min_proy
            ]

        # Filtro por publicaciones - O(1) usando DataCache
        if self.min_publicaciones.strip() and self.min_publicaciones.strip().isdigit():
            min_pub = int(self.min_publicaciones.strip())
            filtered = [
                inv for inv in filtered
                if DataCache.get_publicaciones_count(inv.rut_ir) >= min_pub
            ]

        # Filtro por rol - O(1) usando DataCache
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

    def add_selected_area(self):
        if self.selected_area_temp and self.selected_area_temp not in self.selected_areas:
            self.selected_areas.append(self.selected_area_temp)

    @rx.var
    def get_initials(self) -> str:
        if self.current_investigator_is_none or not self.current_investigator.name:
            return "??"
        name_parts = self.current_investigator.name.split()
        if len(name_parts) >= 2:
            return f"{name_parts[0][0]}{name_parts[1][0]}".upper()
        elif len(name_parts) == 1:
            return name_parts[0][0].upper()
        return "??"

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

    def load_investigador(self, id: int | None = None):
        pass

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
            print("Error: self.current_investigator es None.")
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
            print("Error: self.current_investigator es None.")
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

    def random_selected(self, list_name: str):
        self.selected_items[list_name] = np.random.choice(
            all_items[list_name],
            size=np.random.randint(1, len(all_items[list_name]) + 1),
            replace=False,
        ).tolist()

    @rx.event
    def toggle_filter(self, filter_key: str, value: str):
        if value in self.filtro_cateegorias[filter_key]:
            self.filtro_cateegorias[filter_key].remove(value)
        else:
            self.filtro_cateegorias[filter_key].append(value)

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
            return self.send_user_message_immediate

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
            await asyncio.sleep(0.1)
            from .chatbot.pdf_agent import get_pdf_chatbot_response
            response = get_pdf_chatbot_response(user_input)

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
        import re
        query = self.ai_search_query.lower()
        
        print(f"🔍 AI Search Query: '{query}'")  # Debug

        # Patrones más flexibles para proyectos
        proyecto_patterns = [
            r"(?:más|mas|mayor|mayores)\s*(?:de|que)\s*(\d+)\s*(?:proyectos?|projects?)",
            r"(\d+)\s*(?:o\s*)?(?:más|mas)\s*proyectos?",
            r"(?:al\s*menos|mínimo|minimo|min)\s*(\d+)\s*proyectos?",
            r"(?:con|tengan?|tienen?)\s*(?:más|mas)?\s*(?:de)?\s*(\d+)\s*proyectos?",
            r">\s*(\d+)\s*proyectos?",
            r">=\s*(\d+)\s*proyectos?",
        ]
        
        # Patrones más flexibles para publicaciones
        pub_patterns = [
            r"(?:más|mas|mayor|mayores)\s*(?:de|que)\s*(\d+)\s*(?:publicacion|publicaciones|publications?|papers?|artículos?|articulos?)",
            r"(\d+)\s*(?:o\s*)?(?:más|mas)\s*(?:publicacion|publicaciones|papers?)",
            r"(?:al\s*menos|mínimo|minimo|min)\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
            r"(?:con|tengan?|tienen?)\s*(?:más|mas)?\s*(?:de)?\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
            r">\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
            r">=\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
        ]
        
        rol_co_pattern = r"(?:co-?i\b|co-?\s*investigador[aes]?|coinvestigador[aes]?)"
        rol_ir_pattern = r"(?:\bir\b|investigador[aes]?\s+responsables?|responsables?)"

        detected_areas = []
        applied_filters = []
        
        # Buscar proyectos
        proyecto_match = None
        for pattern in proyecto_patterns:
            proyecto_match = re.search(pattern, query)
            if proyecto_match:
                print(f"✅ Proyecto match con patrón: {pattern}")  # Debug
                break
        
        # Buscar publicaciones  
        pub_match = None
        for pattern in pub_patterns:
            pub_match = re.search(pattern, query)
            if pub_match:
                print(f"✅ Publicaciones match con patrón: {pattern}")  # Debug
                break

        rol_co_match = re.search(rol_co_pattern, query)
        rol_ir_match = re.search(rol_ir_pattern, query)

        if proyecto_match:
            self.min_proyectos = str(int(proyecto_match.group(1)))
            applied_filters.append(f"mínimo {self.min_proyectos} proyectos")
            print(f"✅ min_proyectos = {self.min_proyectos}")  # Debug
        else:
            self.min_proyectos = ""

        if pub_match:
            self.min_publicaciones = str(int(pub_match.group(1)))
            applied_filters.append(f"mínimo {self.min_publicaciones} publicaciones")
            print(f"✅ min_publicaciones = {self.min_publicaciones}")  # Debug
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

        if not (proyecto_match or pub_match or rol_co_match or rol_ir_match):
            self.ai_detected_areas = detected_areas[:3]
            self.selected_areas = detected_areas[:3]
            self.search_term = self.ai_search_query
        else:
            self.ai_detected_areas = []
            self.selected_areas = []
            self.search_term = ""

        if applied_filters:
            self.ai_search_results_summary = f"Filtros aplicados: {', '.join(applied_filters)}"
        else:
            self.ai_search_results_summary = f"Búsqueda por '{self.ai_search_query}'"
        
        print(f"📊 Resumen: {self.ai_search_results_summary}")  # Debug

    def _process_ai_search_response(self, response):
        """Procesa respuesta de IA."""
        try:
            import re
            
            # =====================================================
            # PASO 1: SIEMPRE detectar filtros numéricos primero
            # Esto funciona independiente de la respuesta del agente
            # =====================================================
            query = self.ai_search_query.lower()
            applied_filters = []
            
            print(f"🔍 Procesando AI Search: '{query}'")  # Debug
            
            # Patrones más flexibles para proyectos
            proyecto_patterns = [
                r"(?:más|mas|mayor|mayores)\s*(?:de|que)\s*(\d+)\s*(?:proyectos?|projects?)",
                r"(\d+)\s*(?:o\s*)?(?:más|mas)\s*proyectos?",
                r"(?:al\s*menos|mínimo|minimo|min)\s*(\d+)\s*proyectos?",
                r"(?:con|tengan?|tienen?)\s*(?:más|mas)?\s*(?:de)?\s*(\d+)\s*proyectos?",
                r">\s*(\d+)\s*proyectos?",
                r">=\s*(\d+)\s*proyectos?",
            ]
            min_proy_detected = None
            for pattern in proyecto_patterns:
                match = re.search(pattern, query)
                if match:
                    min_proy_detected = int(match.group(1))
                    print(f"✅ Proyecto detectado: {min_proy_detected}")  # Debug
                    break
            
            # Patrones más flexibles para publicaciones
            pub_patterns = [
                r"(?:más|mas|mayor|mayores)\s*(?:de|que)\s*(\d+)\s*(?:publicacion|publicaciones|publications?|papers?|artículos?|articulos?)",
                r"(\d+)\s*(?:o\s*)?(?:más|mas)\s*(?:publicacion|publicaciones|papers?)",
                r"(?:al\s*menos|mínimo|minimo|min)\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
                r"(?:con|tengan?|tienen?)\s*(?:más|mas)?\s*(?:de)?\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
                r">\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
                r">=\s*(\d+)\s*(?:publicacion|publicaciones|papers?)",
            ]
            min_pub_detected = None
            for pattern in pub_patterns:
                match = re.search(pattern, query)
                if match:
                    min_pub_detected = int(match.group(1))
                    print(f"✅ Publicaciones detectado: {min_pub_detected}")  # Debug
                    break
            
            # Detectar rol
            rol_co_pattern = r"(?:co-?i\b|co-?\s*investigador[aes]?|coinvestigador[aes]?)"
            rol_ir_pattern = r"(?:\bir\b|investigador[aes]?\s+responsables?|responsables?|principales?)"
            
            rol_detected = None
            if re.search(rol_co_pattern, query):
                rol_detected = "co-i"
            elif re.search(rol_ir_pattern, query):
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
            
            print(f"📊 Filtros aplicados: {applied_filters}")  # Debug

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
            
            # Construir resumen
            if applied_filters:
                self.ai_search_results_summary = f"Filtros aplicados: {', '.join(applied_filters)}"
            elif summary:
                self.ai_search_results_summary = summary
            else:
                self.ai_search_results_summary = f"Búsqueda por '{self.ai_search_query}'"

        except Exception as e:
            print(f"❌ Error en _process_ai_search_response: {e}")  # Debug
            self.ai_search_error = f"Error procesando respuesta: {str(e)}"
            self._perform_simple_ai_search()

    @rx.event
    def clear_ai_detected_areas(self):
        self.ai_detected_areas = []
        self.ai_search_results_summary = ""