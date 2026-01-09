import reflex as rx
import asyncio
from .data_items import all_items
import pandas as pd
import numpy as np
from .models import Investigador, Publicaciones, Proyectos
from typing import Dict, List, Optional


proyectos_csv = "proyectos_total.xlsx"

# academicas_csv = "academicas_clean.csv"
academicas_csv = "academicas.xlsx"

publicaciones_csv = "publicaciones_total.xlsx"


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

    # Búsqueda por cantidad mínima de proyectos y publicaciones
    min_proyectos: str = ""
    min_publicaciones: str = ""

    # Búsqueda por rol en proyectos
    search_rol: str = ""

    total_items: int = 0
    total_investigadores: int = 0
    offset: int = 0
    limit: int = 24  # Number of rows per page

    name: str = ""
    institucion: str = ""
    email: str = ""
    city: str = ""
    message: str = ""

    selected_items: Dict[str, List] = (
        all_items  # We add all items to the selected items by default
    )

    # 13/01/2025
    # Áreas disponibles y seleccionadas (ajústalas a tu gusto)
    # all_areas: list[str] = ["IA", "Biotecnología", "Big Data"]
    all_areas: list[str] = []
    selected_areas: list[str] = []

    selected_area: str = ""

    selected_area_temp: str = ""

    chatbot_messages: List[Dict[str, str]] = []
    chatbot_input: str = ""
    chatbot_status: str = "not_initialized"
    chatbot_session_id: Optional[str] = None
    chatbot_is_loading: bool = False
    chatbot_error: str = ""

    # AI Search - Separación de estados para evitar renders innecesarios
    ai_search_input: str = ""  # Solo para mostrar lo que escribe el usuario
    ai_search_query: str = ""  # Solo se actualiza cuando busca explícitamente
    ai_search_loading: bool = False
    ai_search_error: str = ""
    ai_search_results_summary: str = ""
    ai_detected_areas: list[str] = []

    # Cache para optimizar get_investigator_counts()
    _cached_publicaciones_counts: dict = {}
    _cached_proyectos_counts: dict = {}

    @rx.event
    def next_image(self):
        """Go to the next image in the carousel."""
        self.current_index = (self.current_index + 1) % len(self.image_urls)

    @rx.event
    def prev_image(self):
        """Go to the previous image in the carousel."""
        self.current_index = (self.current_index - 1 + len(self.image_urls)) % len(
            self.image_urls
        )

    @rx.event(background=True)
    async def start_autoscroll(self):
        """Start the autoscroll background task."""
        while True:
            await asyncio.sleep(8)
            async with self:
                self.current_index = (self.current_index + 1) % len(self.image_urls)

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
        self.selected_areas = list(self.all_areas).sort()

    @rx.event
    def clear_areas(self):
        self.selected_areas.clear()

    @rx.var
    def year_list(self) -> list:
        return self.filtered_year

    @rx.var
    def filtered_investigators(self) -> list[Investigador]:
        term = self.search_term.lower().strip()

        if term:
            filtered = [
                inv
                for inv in self.investigadores
                if (term in str(inv.id))
                or (term in inv.name.lower())
                or (term in inv.ocde_2.lower())
                # or (term in inv.titulo.lower())
                # or (term in inv.programa.lower())
            ]
        else:
            filtered = self.investigadores

        # Filtro por áreas OCDE seleccionadas
        if self.selected_areas:
            filtered = [
                inv
                for inv in filtered
                if all(area in inv.ocde_2 for area in self.selected_areas)
            ]

        # Filtro por cantidad mínima de proyectos
        if self.min_proyectos.strip() and self.min_proyectos.strip().isdigit():
            min_proy = int(self.min_proyectos.strip())
            filtered = [
                inv
                for inv in filtered
                if self.get_investigator_counts(inv)["proyectos"] >= min_proy
            ]

        # Filtro por cantidad mínima de publicaciones
        if self.min_publicaciones.strip() and self.min_publicaciones.strip().isdigit():
            min_pub = int(self.min_publicaciones.strip())
            filtered = [
                inv
                for inv in filtered
                if self.get_investigator_counts(inv)["publicaciones"] >= min_pub
            ]

        # Filtro por rol en proyectos
        if self.search_rol.strip():
            filtered = [
                inv
                for inv in filtered
                if self.investigator_has_rol(inv, self.search_rol.strip())
            ]

        return filtered

    @rx.var
    def sorted_areas(self) -> list[str]:
        return sorted([a for a in self.all_areas if a.strip()])

    @rx.var
    def sorted_selected_areas(self) -> list[str]:
        return sorted(self.selected_areas)

    def add_selected_area(self):
        if (
            self.selected_area_temp
            and self.selected_area_temp not in self.selected_areas
        ):
            self.selected_areas.append(self.selected_area_temp)

    @rx.var
    def get_initials(self) -> str:
        if self.current_investigator_is_none or not self.current_investigator.name:
            return "??"

        name_parts = self.current_investigator.name.split()

        if len(name_parts) >= 2:
            # Nombre + apellido1: toma primera letra del nombre y primera del apellido1
            return f"{name_parts[0][0]}{name_parts[1][0]}".upper()
        elif len(name_parts) == 1:
            # Solo nombre: toma primera letra
            return name_parts[0][0].upper()
        else:
            return "??"

    @rx.event
    def load_grid_data(self):
        if self.current_investigator:
            df_proyectos = pd.read_excel(proyectos_csv)
            df_publicaciones = pd.read_excel(publicaciones_csv)
            # Filter your dataframe based on current_investigator
            filtered_data = df_proyectos[
                df_proyectos["rut_ir"] == self.current_investigator.rut_ir
            ]

            filtered_pub = df_publicaciones[
                df_publicaciones["rut_ir"] == self.current_investigator.rut_ir
            ]

            filtered_year = df_proyectos[
                df_proyectos["rut_ir"] == self.current_investigator.rut_ir
            ]["año"]

            self.grid_data = filtered_data.to_dict("records")
            self.grid_data2 = filtered_pub.to_dict("records")
            self.filtered_count = int(len(filtered_data))
            self.filtered_year = filtered_year.to_list()
            self.filtered_count_pub = int(len(filtered_pub))

    def set_search_term(self, term: str):
        """Actualiza la búsqueda."""
        self.search_term = term

    @rx.event
    def set_min_proyectos(self, value: str):
        """Establece el filtro de cantidad mínima de proyectos."""
        # Validación: solo permitir números positivos
        if value.strip() == "":
            self.min_proyectos = ""
        elif value.strip().isdigit() and int(value.strip()) >= 0:
            self.min_proyectos = value.strip()
        # Si no es válido, mantener el valor anterior (no hacer nada)

    @rx.event
    def set_min_publicaciones(self, value: str):
        """Establece el filtro de cantidad mínima de publicaciones."""
        # Validación: solo permitir números positivos
        if value.strip() == "":
            self.min_publicaciones = ""
        elif value.strip().isdigit() and int(value.strip()) >= 0:
            self.min_publicaciones = value.strip()
        # Si no es válido, mantener el valor anterior (no hacer nada)

    @rx.event
    def set_search_rol(self, value: str):
        """Establece el filtro de búsqueda por rol."""
        # Validación: limpiar espacios en blanco
        self.search_rol = value.strip()

    @rx.var(cache=True)
    def search_results_empty(self) -> bool:
        """Indica si los resultados de búsqueda están vacíos."""
        return len(self.filtered_investigators) == 0

    @rx.var(cache=True)
    def search_message(self) -> str:
        """Mensaje para mostrar información sobre la búsqueda."""
        total = len(self.filtered_investigators)
        if total == 0:
            if (
                self.search_term.strip()
                or self.min_proyectos.strip()
                or self.min_publicaciones.strip()
                or self.search_rol.strip()
                or self.selected_areas
            ):
                return "No se encontraron investigadoras que coincidan con los filtros aplicados."
            else:
                return "No hay datos disponibles."
        else:
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
        inv = next((x for x in self.investigators if x["id"] == id), None)
        # self.current_investigator = inv  # Comentado: current_investigator es ahora computed var

    @rx.var
    def current_investigator_is_none(self) -> bool:
        return self.current_investigator is None

    @rx.event
    def load_academicas(self):
        # df = pd.read_csv(academicas_csv, encoding="ISO-8859-1")
        # df = pd.read_csv(academicas_csv, delimiter="," ,encoding="ISO-8859-1")
        df = pd.read_excel(academicas_csv)

        df = df.replace("", None)
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"])  # Elimina filas con NaN en "id"

        df["id"] = df["id"].astype(int)
        df["orcid"] = df["orcid"].fillna("")
        df["grado_mayor"] = df["grado_mayor"].astype(str)
        # df["grado_mayor"] = df["grado_mayor"].fillna("Investigadora")
        df["grado_mayor"] = df["grado_mayor"].replace("nan", "INVESTIGADORA")
        df["grado_mayor"] = df["grado_mayor"].replace("", "INVESTIGADORA")
        # df["grado_mayor"] = df["grado_mayor"].fillna("")
        # df["unidad_contrato"] = df["unidad_contrato"].fillna("")
        df["ocde_2"] = (
            df["ocde_2"]
            .astype(str)
            .apply(lambda x: " ,".join(x.split("#")) if x and x != "nan" else [])
        )
        # df["ocde_2"] = df["ocde_2"].astype(str).apply(lambda x: x.split("#") if x and x != "nan" else [])

        # df["ocde_2"] = df["ocde_2"].astype(str).apply(lambda x: ", ".join(x.split("#")) if x and x != "nan" else "")

        # df["ocde_2"] = (
        #     df["ocde_2"]
        #     .astype(str)
        #     .apply(lambda x: [s.strip() for s in x.split("#")] if x and x != "nan" else [])
        # )

        self.investigadores = [
            Investigador(**row.to_dict()) for _, row in df.iterrows()
        ]

        # self.investigadores = [Investigador(**row.to_dict()) for _, row in df.iterrows()]
        self.total_investigadores = len(self.investigadores)

        self.all_areas = sorted(
            df["ocde_2"].dropna().str.split(",").explode().str.strip().unique().tolist()
        )

        # Precargar datos de proyectos y publicaciones para mejorar rendimiento de búsquedas
        try:
            self._preload_search_data()
        except Exception as e:
            print(f"Error en preload search data: {e}")

    def _preload_search_data(self):
        """Preload search data to improve performance."""
        try:
            import pandas as pd

            # Precargar datos de proyectos y publicaciones
            df_proyectos = pd.read_excel(proyectos_csv)
            df_publicaciones = pd.read_excel(publicaciones_csv)

            # Inicializar cache
            self._cached_proyectos_counts = {}
            self._cached_publicaciones_counts = {}

            # Pre-calcular conteos
            for rut in df_proyectos["rut_ir"].unique():
                if pd.notna(rut):
                    count = len(df_proyectos[df_proyectos["rut_ir"] == rut])
                    self._cached_proyectos_counts[str(rut)] = count

            for rut in df_publicaciones["rut_ir"].unique():
                if pd.notna(rut):
                    count = len(df_publicaciones[df_publicaciones["rut_ir"] == rut])
                    self._cached_publicaciones_counts[str(rut)] = count

        except Exception as e:
            print(f"Error preloading search data: {e}")
            self._cached_proyectos_counts = {}
            self._cached_publicaciones_counts = {}

    def get_investigator_counts(self, investigador: Investigador) -> dict:
        """Calcula la cantidad de proyectos y publicaciones para un investigador usando cache."""
        try:
            # Usar datos precargados para evitar recargar CSVs constantemente
            if (
                not self._cached_proyectos_counts
                or not self._cached_publicaciones_counts
            ):
                import pandas as pd

                df_proyectos = pd.read_excel(proyectos_csv)
                df_publicaciones = pd.read_excel(publicaciones_csv)

                # Inicializar cache vacío ANTES de llenar
                self._cached_proyectos_counts = {}
                self._cached_publicaciones_counts = {}

                # Pre-calcular conteos para todos los RUTs únicos
                for rut in df_proyectos["rut_ir"].unique():
                    count = len(df_proyectos[df_proyectos["rut_ir"] == rut])
                    self._cached_proyectos_counts[str(rut)] = count

                for rut in df_publicaciones["rut_ir"].unique():
                    count = len(df_publicaciones[df_publicaciones["rut_ir"] == rut])
                    self._cached_publicaciones_counts[str(rut)] = count

            # Usar cache para obtener conteos
            rut_str = str(investigador.rut_ir)
            proyectos_count = self._cached_proyectos_counts.get(rut_str, 0)
            publicaciones_count = self._cached_publicaciones_counts.get(rut_str, 0)

            return {"proyectos": proyectos_count, "publicaciones": publicaciones_count}
        except Exception as e:
            print(f"Error calculating counts for {investigador.name}: {e}")
            return {"proyectos": 0, "publicaciones": 0}

    def investigator_has_rol(self, investigador: Investigador, search_rol: str) -> bool:
        """Verifica si un investigador tiene un rol específico en sus proyectos."""
        try:
            import pandas as pd

            df_proyectos = pd.read_excel(proyectos_csv)

            # Buscar proyectos del investigador
            investigador_proyectos = df_proyectos[
                df_proyectos["rut_ir"] == investigador.rut_ir
            ]

            # Si no tiene proyectos, no puede tener roles - CORREGIDO
            if len(investigador_proyectos) == 0:
                return False

            # Buscar el rol en los proyectos del investigador
            search_rol_lower = search_rol.lower()

            # Términos comunes para roles
            rol_mapping = {
                "ir": "investigador responsable",
                "co-i": "co-investigador",
                "coinvestigador": "co-investigador",
                "co investigador": "co-investigador",
                "investigador responsable": "investigador responsable",
                "responsable": "investigador responsable",
            }

            # Aplicar mapeo si existe
            search_rol_final = rol_mapping.get(search_rol_lower, search_rol_lower)

            for _, proyecto in investigador_proyectos.iterrows():
                rol_proyecto = str(proyecto.get("rol", "")).lower()
                if (
                    search_rol_lower in rol_proyecto
                    or search_rol_final in rol_proyecto
                    or any(term in rol_proyecto for term in search_rol_lower.split())
                ):
                    return True

            return False
        except Exception as e:
            print(f"Error checking rol for {investigador.name}: {e}")
            return False

    # def load_investigador(self, id: int):
    #     # Este método se invocará cuando el usuario visite /investigador/<id>.
    #     inv = next((x for x in self.investigators if x["id"] == id), None)
    #     self.current_inv = inv

    @rx.var
    def total_proyectos(self) -> int:
        return len(self.proyectos)

    @rx.var
    def filtered_sorted_proyectos(self) -> list[Proyectos]:
        proyectos = self.proyectos
        if self.search_value_proy:
            search_value = self.search_value_proy.lower()
            proyectos = [
                proyecto
                for proyecto in proyectos
                if any(
                    search_value in str(getattr(proyecto, attr)).lower()
                    for attr in [
                        "codigo",
                        "titulo",
                        "año",
                        "ocde_2",
                        "tipo_proyecto",
                        "investigador_responsable",
                        "rol",
                    ]
                )
            ]
        return proyectos

    @rx.var
    def filtered_sorted_pub(self) -> list[Publicaciones]:
        publicaciones = self.publicaciones
        if self.search_value_pub:
            search_value = self.search_value_pub.lower()
            publicaciones = [
                publicacion
                for publicacion in publicaciones
                if any(
                    search_value in str(getattr(publicacion, attr)).lower()
                    for attr in [
                        "año",
                        "titulo",
                        "revista",
                        "cuartil",
                        "autor",
                        "wos_id",
                        "liderado",
                        "url",
                    ]
                )
            ]
        return publicaciones

    @rx.var
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.var
    def total_pages(self) -> int:
        return (self.total_items // self.limit) + (
            1 if self.total_items % self.limit else 0
        )

    @rx.var(initial_value=[])
    def get_current_page(self) -> list[Proyectos]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_proyectos[start_index:end_index]

    @rx.var(initial_value=[])
    def get_current_page_pub(self) -> list[Publicaciones]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_pub[start_index:end_index]

    def prev_page(self):
        if self.page_number > 1:
            self.offset -= self.limit

    def next_page(self):
        if self.page_number < self.total_pages:
            self.offset += self.limit

    def first_page(self):
        self.offset = 0

    def last_page(self):
        self.offset = (self.total_pages - 1) * self.limit

    def load_entries(self):
        if self.current_investigator is None:
            print(
                "Error: self.current_investigator es None. No se pueden cargar proyectos."
            )
            return
        # if self.current_investigator is None:
        #     return
        df = pd.read_excel(proyectos_csv)
        df = df.replace("", np.nan)  # Replace empty strings with NaN
        df.columns = df.columns.str.strip()

        # if isinstance(proyectos_csv, str):
        #     df = pd.read_csv(proyectos_csv)
        # else:
        #     df = proyectos_csv.copy()

        # Verifica que las columnas existan
        # if "rut_ir" not in df.columns:
        #     raise ValueError("El DataFrame no contiene la columna 'rut_ir'")

        # rut_actual = str(self.current_investigator.rut_ir).strip()
        # df["rut_ir"] = df["rut_ir"].astype(str).str.strip()
        # df = df[df["rut_ir"] == rut_actual].copy()

        df = df[df["rut_ir"] == self.current_investigator.rut_ir]
        # df["ocde_1"] = df["ocde_1"].fillna("SIN INFO")
        df["ocde_2"] = df["ocde_2"].fillna("SIN INFO")
        # df["ocde_1"] = df["ocde_1"].fillna("Sin Info")
        # df["rol"] = df["rol"].astype(str).str.replace(";", "", regex=False).str.strip()
        # df["rol"] = df["rol"].replace("", "Sin rol")
        df["rol"] = df["rol"].fillna("Sin Info")
        # df["año"] = df["año"].astype(int)
        df["año"] = pd.to_numeric(df["año"], errors="coerce")
        df["año"] = df["año"].fillna(0).astype(int)
        self.proyectos = [Proyectos(**row) for _, row in df.iterrows()]
        self.total_items = len(self.proyectos)

    def load_entries_pub(self):
        if self.current_investigator is None:
            print(
                "Error: self.current_investigator es None. No se pueden cargar publicaciones."
            )
            return  # Salir de la función si no hay investigador seleccionado

        df = pd.read_excel(publicaciones_csv)
        df = df.replace("", np.nan)
        df = df[df["rut_ir"] == self.current_investigator.rut_ir]
        df["doi"] = df["doi"].astype(str)
        df["doi"] = df["doi"].replace("nan", "")
        self.publicaciones = [Publicaciones(**row) for _, row in df.iterrows()]

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()

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
        """Agrega o elimina un valor del filtro."""
        if value in self.filtro_cateegorias[filter_key]:
            # Si ya está seleccionado, lo quitamos
            self.filtro_cateegorias[filter_key].remove(value)
        else:
            # Si no está seleccionado, lo agregamos
            self.filtro_cateegorias[filter_key].append(value)

    # Chatbot functionality
    @rx.event(background=True)
    async def initialize_chatbot(self):
        """Initialize the PDF chatbot agent."""
        async with self:
            try:
                self.chatbot_status = "initializing"
                self.chatbot_error = ""

                from .chatbot.pdf_agent import (
                    is_pdf_chatbot_ready,
                    get_pdf_chatbot_info,
                )

                if is_pdf_chatbot_ready():
                    self.chatbot_status = "ready"
                    self.chatbot_messages = [
                        {
                            "role": "assistant",
                            "content": "¡Hola! Soy tu asistente para consultas sobre documentos del Observatorio OCDE. Puedo responder preguntas basándome únicamente en los documentos PDF disponibles. ¿En qué puedo ayudarte?",
                        }
                    ]
                else:
                    self.chatbot_status = "error"
                    info = get_pdf_chatbot_info()
                    if not info.get("ready", False):
                        self.chatbot_error = "No se pudo inicializar el chatbot. Verifique ANTHROPIC_API_KEY y documentos PDF."

            except Exception as e:
                self.chatbot_status = "error"
                self.chatbot_error = f"Error al inicializar: {str(e)}"

    @rx.event
    def set_chatbot_input(self, value: str):
        """Set the chatbot input value."""
        self.chatbot_input = value

    @rx.event
    def handle_chatbot_key_press(self, key: str):
        """Handle key press in chatbot input."""
        if (
            key == "Enter"
            and not self.chatbot_is_loading
            and self.chatbot_input.strip()
        ):
            return self.send_user_message_immediate

    @rx.event
    def send_user_message_immediate(self):
        """Send user message and start loading immediately."""
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
        """Process AI response in background."""
        try:
            # Pequeña pausa para asegurar que el loading se vea
            import asyncio

            await asyncio.sleep(0.1)

            from .chatbot.pdf_agent import get_pdf_chatbot_response

            # Procesar respuesta de IA
            response = get_pdf_chatbot_response(user_input)

            # Actualizar estado con respuesta de IA
            async with self:
                assistant_message = {"role": "assistant", "content": response}
                self.chatbot_messages.append(assistant_message)

        except Exception as e:
            async with self:
                self.chatbot_error = f"Error: {str(e)}"
                # Remover mensaje del usuario si hubo error
                if (
                    self.chatbot_messages
                    and self.chatbot_messages[-1]["role"] == "user"
                ):
                    self.chatbot_messages.pop()

        finally:
            async with self:
                self.chatbot_is_loading = False

    # Search functionality
    @rx.event
    def set_ai_search_input(self, value: str):
        """
        SÚPER OPTIMIZADO: Solo actualiza el texto visible,
        SIN triggear búsquedas ni renders de datos.
        Escritura instantánea garantizada.
        """
        self.ai_search_input = value

    @rx.event
    def set_ai_search_query(self, query: str):
        self.ai_search_input = query

    @rx.event
    def handle_ai_search_enter(self, key: str):
        """Enter key optimizado - solo busca cuando presiona Enter."""
        if key == "Enter":
            return self.perform_ai_search

    @rx.event(background=True)
    async def perform_ai_search(self):
        """
        BÚSQUEDA BAJO DEMANDA: Solo se ejecuta cuando el usuario
        explícitamente presiona Enter o el botón Buscar.
        CERO renders mientras escribe.
        """
        async with self:
            search_text = self.ai_search_input.strip()
            if not search_text:
                # Si el campo está vacío, limpiar TODOS los filtros y mostrar todas las investigadoras
                self.search_term = ""
                self.selected_areas = []
                self.ai_detected_areas = []
                self.min_proyectos = ""
                self.min_publicaciones = ""
                self.search_rol = ""
                self.ai_search_results_summary = (
                    "Mostrando todas las investigadoras (409 total)"
                )
                self.ai_search_error = ""
                return

            self.ai_search_query = search_text
            self.ai_search_loading = True
            self.ai_search_error = ""
            self.ai_search_results_summary = ""

        try:
            from .chatbot.ai_search_agent import (
                get_ai_search_response,
                is_ai_search_ready,
            )

            if not is_ai_search_ready():
                # Agregar delay para hacer visible el loading
                await asyncio.sleep(0.5)
                async with self:
                    self._perform_simple_ai_search()
            else:
                # Agregar un pequeño delay para hacer visible el loading
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
        """Fallback simple search cuando AI no está disponible con detección de filtros numéricos y roles."""
        query = self.ai_search_query.lower()

        # Detectar patrones de cantidad de proyectos
        import re

        # Patrones simplificados que detectan "mas/más de X" con y sin tilde
        proyecto_pattern = r"(?:más|mas)\s+de\s+(\d+)\s*(?:proyectos?|projects?)"
        pub_pattern = (
            r"(?:más|mas)\s+de\s+(\d+)\s*(?:publicaciones?|publications?|papers?)"
        )

        # Patrones expandidos para roles
        # Patrón CO-I: co-investigador, coinvestigador, rol co-i, investigadoras co-i, etc.
        rol_co_pattern = r"(?:co-?i\b|\bco\s+i\b|co-?\s*investigador[aes]?|coinvestigador[aes]?|rol\s+(?:de\s+)?co-?i\b|con\s+rol\s+co-?i\b|rol\s+(?:de\s+)?co-?\s*investigador[aes]?|con\s+rol\s+co-?\s*investigador[aes]?|investigador[aes]?\s+co-?i\b|investigador[aes]?\s+co-?\s*investigador[aes]?|investigador[aes]?\s+con\s+rol\s+co|investigador[aes]?\s+de\s+co|investigador[aes]?\s+co\b|\bco\s+investigador[aes]?)"

        # Patrón IR: investigador responsable, rol ir, investigadoras ir, líder de proyecto, etc.
        rol_ir_pattern = r"(?:\bir\b|i\.?\s*r\.?|investigador[aes]?\s+responsables?|investigador[aes]?\s+principales?|responsables?\s+de\s+(?:la\s+)?investigaci[oó]n|principales?\s+de\s+(?:la\s+)?investigaci[oó]n|rol\s+(?:de\s+)?ir\b|con\s+rol\s+ir\b|rol\s+(?:de\s+)?investigador[aes]?\s+responsables?|rol\s+(?:de\s+)?investigador[aes]?\s+principales?|con\s+rol\s+(?:investigador[aes]?\s+)?responsables?|con\s+rol\s+(?:investigador[aes]?\s+)?principales?|investigador[aes]?\s+ir\b|investigador[aes]?\s+con\s+rol\s+(?:ir\b|responsables?|principales?)|(?:responsables?|l[íi]deres?)\s+de\s+(?:proyecto|investigaci[oó]n)|investigador[aes]?\s+(?:de|del)\s+proyecto|investigador[aes]?\s+responsables?|investigador[aes]?\s+principales?|responsables?\s+(?=.*investigador)|principales?\s+(?=.*investigador))"

        # Buscar cantidades en la consulta
        proyecto_match = re.search(proyecto_pattern, query)
        pub_match = re.search(pub_pattern, query)
        rol_co_match = re.search(rol_co_pattern, query)
        rol_ir_match = re.search(rol_ir_pattern, query)

        detected_areas = []
        applied_filters = []

        # Aplicar filtro de proyectos si se detecta
        if proyecto_match:
            min_proyectos = int(proyecto_match.group(1))
            self.min_proyectos = str(min_proyectos)
            applied_filters.append(f"mínimo {min_proyectos} proyectos")
        else:
            self.min_proyectos = ""

        # Aplicar filtro de publicaciones si se detecta
        if pub_match:
            min_publicaciones = int(pub_match.group(1))
            self.min_publicaciones = str(min_publicaciones)
            applied_filters.append(f"mínimo {min_publicaciones} publicaciones")
        else:
            self.min_publicaciones = ""

        # Aplicar filtro de rol si se detecta
        if rol_co_match:
            self.search_rol = "co-i"
            applied_filters.append("rol co-investigador")
        elif rol_ir_match:
            self.search_rol = "ir"
            applied_filters.append("rol investigador responsable")
        else:
            self.search_rol = ""

        # Detectar áreas OCDE en la consulta
        for area in self.all_areas:
            if any(word in area.lower() for word in query.split()):
                detected_areas.append(area)

        # Solo aplicar filtros de área si no hay filtros numéricos o de rol más específicos
        if not (proyecto_match or pub_match or rol_co_match or rol_ir_match):
            self.ai_detected_areas = detected_areas[:3]
            self.selected_areas = detected_areas[:3]
            self.search_term = self.ai_search_query
        else:
            # Limpiar otros filtros para enfocarse en filtros específicos (números o roles)
            self.ai_detected_areas = []
            self.selected_areas = []
            self.search_term = ""

        # Crear resumen de filtros aplicados
        if applied_filters:
            filters_text = " y ".join(applied_filters)
            areas_text = (
                f" en {len(detected_areas)} áreas relacionadas"
                if detected_areas
                else ""
            )
            self.ai_search_results_summary = (
                f"Buscando investigadoras con {filters_text}{areas_text}."
            )
        else:
            self.ai_search_results_summary = f"Búsqueda simple por '{self.ai_search_query}'. Encontradas {len(detected_areas)} áreas relacionadas."

    def _process_ai_search_response(self, response):
        """Process AI response and update search filters with auto-detection intelligence."""
        try:
            if isinstance(response, dict):
                data = response
            else:
                import json

                response_str = str(response)
                start = response_str.find("{")
                end = response_str.rfind("}") + 1
                if start != -1 and end != 0:
                    json_str = response_str[start:end]
                    data = json.loads(json_str)
                else:
                    self._perform_simple_ai_search()
                    return

            # PRIMERO: Detectar filtros numéricos en la consulta original
            import re

            query_original = self.ai_search_query.lower()

            # Patrones de filtros numéricos
            proyecto_pattern = r"(?:más|mas)\s+de\s+(\d+)\s*(?:proyectos?|projects?)"
            pub_pattern = (
                r"(?:más|mas)\s+de\s+(\d+)\s*(?:publicaciones?|publications?|papers?)"
            )

            # Patrones expandidos para roles
            # Patrón CO-I: co-investigador, coinvestigador, rol co-i, investigadoras co-i, etc.
            rol_co_pattern = r"(?:co-?i\b|\bco\s+i\b|co-?\s*investigador[aes]?|coinvestigador[aes]?|rol\s+(?:de\s+)?co-?i\b|con\s+rol\s+co-?i\b|rol\s+(?:de\s+)?co-?\s*investigador[aes]?|con\s+rol\s+co-?\s*investigador[aes]?|investigador[aes]?\s+co-?i\b|investigador[aes]?\s+co-?\s*investigador[aes]?|investigador[aes]?\s+con\s+rol\s+co|investigador[aes]?\s+de\s+co|investigador[aes]?\s+co\b|\bco\s+investigador[aes]?)"

            # Patrón IR: investigador responsable, rol ir, investigadoras ir, líder de proyecto, etc.
            rol_ir_pattern = r"(?:\bir\b|i\.?\s*r\.?|investigador[aes]?\s+responsables?|investigador[aes]?\s+principales?|responsables?\s+de\s+(?:la\s+)?investigaci[oó]n|principales?\s+de\s+(?:la\s+)?investigaci[oó]n|rol\s+(?:de\s+)?ir\b|con\s+rol\s+ir\b|rol\s+(?:de\s+)?investigador[aes]?\s+responsables?|rol\s+(?:de\s+)?investigador[aes]?\s+principales?|con\s+rol\s+(?:investigador[aes]?\s+)?responsables?|con\s+rol\s+(?:investigador[aes]?\s+)?principales?|investigador[aes]?\s+ir\b|investigador[aes]?\s+con\s+rol\s+(?:ir\b|responsables?|principales?)|(?:responsables?|l[íi]deres?)\s+de\s+(?:proyecto|investigaci[oó]n)|investigador[aes]?\s+(?:de|del)\s+proyecto|investigador[aes]?\s+responsables?|investigador[aes]?\s+principales?|responsables?\s+(?=.*investigador)|principales?\s+(?=.*investigador))"

            proyecto_match = re.search(proyecto_pattern, query_original)
            pub_match = re.search(pub_pattern, query_original)
            rol_co_match = re.search(rol_co_pattern, query_original)
            rol_ir_match = re.search(rol_ir_pattern, query_original)

            if proyecto_match or pub_match or rol_co_match or rol_ir_match:
                self._perform_simple_ai_search()
                return

            tipo_busqueda = data.get("tipo_busqueda", "area")
            detected_areas = data.get("areas_detectadas", [])
            detected_names = data.get("nombres_detectados", [])
            detected_titles = data.get("titulos_detectados", [])
            search_terms = data.get("terminos_busqueda", [])
            summary = data.get("resumen", "")

            valid_areas = [area for area in detected_areas if area in self.all_areas]

            if tipo_busqueda == "nombre":
                self.search_term = (
                    " ".join(detected_names) if detected_names else self.ai_search_query
                )
                self.selected_areas = []
                self.ai_detected_areas = []

            elif tipo_busqueda == "area":
                self.selected_areas = valid_areas
                self.ai_detected_areas = valid_areas
                self.search_term = ""

            elif tipo_busqueda == "titulo":
                title_terms = " ".join(detected_titles) if detected_titles else ""
                general_terms = " ".join(search_terms) if search_terms else ""
                combined_terms = f"{title_terms} {general_terms}".strip()

                self.search_term = combined_terms or self.ai_search_query
                self.selected_areas = []
                self.ai_detected_areas = []

            elif tipo_busqueda == "hibrida":
                name_terms = " ".join(detected_names) if detected_names else ""
                title_terms = " ".join(detected_titles) if detected_titles else ""
                general_terms = " ".join(search_terms) if search_terms else ""
                combined_terms = f"{name_terms} {title_terms} {general_terms}".strip()

                self.search_term = combined_terms or self.ai_search_query
                self.selected_areas = valid_areas
                self.ai_detected_areas = valid_areas

            else:
                self.ai_detected_areas = valid_areas
                self.selected_areas = valid_areas
                self.search_term = (
                    " ".join(search_terms) if search_terms else self.ai_search_query
                )
            self.ai_search_results_summary = summary

        except Exception as e:
            self.ai_search_error = f"Error procesando respuesta: {str(e)}"
            self._perform_simple_ai_search()

    @rx.event
    def clear_ai_detected_areas(self):
        """Clear AI detected areas."""
        self.ai_detected_areas = []
        self.ai_search_results_summary = ""

    # def load_grid_data(self):
    #     if self.current_investigator:
    #         # Filter your dataframe based on current_investigator
    #         filtered_data = df_proyectos[df_proyectos["rut_ir"] == self.current_investigator.rut_ir]
    #         self.grid_data = filtered_data.to_dict("records")