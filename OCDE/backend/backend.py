import reflex as rx
from .data_items import all_items
import pandas as pd
import numpy as np
from typing import List, Dict
from .models import Investigador, Publicaciones, Proyectos
from typing import Optional
from typing import Dict

proyectos_csv = "proyectos_total_ocde1_.csv"

academicas_csv = "academicas_clean.csv"

publicaciones_csv = "publicaciones___.csv"

# df_publicaciones = pd.read_csv(publicaciones_csv, encoding="utf-8-sig")


# total_publicaciones_22 = len(df_publicaciones[df_publicaciones["año"] == 2022])
# total_publicaciones_21 = len(df_publicaciones[df_publicaciones["año"] == 2021])

# #hacer conteo total de proyectos
# total_proyectos = len(df_proyectos)
# #hacer conteo de proyectos por años desde 2018 a 2023, valor int
# # proyectos_2018 = len(df_proyectos[df_proyectos["año"] == 2018])
# # proyectos_2019 = len(df_proyectos[df_proyectos["año"] == 2019])
# # proyectos_2020 = len(df_proyectos[df_proyectos["año"] == 2020])
# # proyectos_2021 = len(df_proyectos[df_proyectos["año"] == 2021])
# # proyectos_2022 = len(df_proyectos[df_proyectos["año"] == 2022])
# proyectos_2023 = len(df_proyectos[df_proyectos["año"] == 2023])
# proyectos_2024 = len(df_proyectos[df_proyectos["año"] == 2024])

# #conteo de investigadores unicos en la columna investigador_responsable
# investigadores = len(df_proyectos["investigador_responsable"].unique())
# inv_2018 = len(df_proyectos[df_proyectos["año"] == 2018]["investigador_responsable"].unique())
# inv_2019 = len(df_proyectos[df_proyectos["año"] == 2019]["investigador_responsable"].unique())
# inv_2020 = len(df_proyectos[df_proyectos["año"] == 2020]["investigador_responsable"].unique())
# inv_2021 = len(df_proyectos[df_proyectos["año"] == 2021]["investigador_responsable"].unique())
# inv_2022 = len(df_proyectos[df_proyectos["año"] == 2022]["investigador_responsable"].unique())
# inv_2023 = len(df_proyectos[df_proyectos["año"] == 2023]["investigador_responsable"].unique())
# inv_2024 = len(df_proyectos[df_proyectos["año"] == 2024]["investigador_responsable"].unique())

# #conteo de disciplinas unicas en la columna disciplina
# disciplinas = len(df_proyectos["ocde_1"].unique())
# ciencias_agricolas = len(df_proyectos[df_proyectos["ocde_1"] == "Ciencias Agrícolas"])
# #ciencias agricolas del 2023
# ciencias_agricolas_2023 = len(df_proyectos[(df_proyectos["ocde_1"] == "CIENCIAS AGRÍCOLAS") & (df_proyectos["año"] == 2023)])
# ciencias_agricolas_2024 = len(df_proyectos[(df_proyectos["ocde_1"] == "CIENCIAS AGRÍCOLAS") & (df_proyectos["año"] == 2024)])

# #ciencias naturales del 2023
# ciencias_naturales_2023 = len(df_proyectos[(df_proyectos["ocde_1"] == "CIENCIAS NATURALES") & (df_proyectos["año"] == 2023)])
# ciencias_naturales_2024 = len(df_proyectos[(df_proyectos["ocde_1"] == "CIENCIAS NATURALES") & (df_proyectos["año"] == 2024)])

# #ciencias sociales del 2023
# ciencias_sociales_2023 = len(df_proyectos[(df_proyectos["ocde_1"] == "CIENCIAS SOCIALES") & (df_proyectos["año"] == 2023)])
# ciencias_sociales_2024 = len(df_proyectos[(df_proyectos["ocde_1"] == "CIENCIAS SOCIALES") & (df_proyectos["año"] == 2024)])

# #ingenieria y tecnologia del 2023
# ingenieria_tecnologia_2023 = len(df_proyectos[(df_proyectos["ocde_1"] == "INGENIERÍA Y TECNOLOGÍA") & (df_proyectos["año"] == 2023)])
# ingenieria_tecnologia_2024 = len(df_proyectos[(df_proyectos["ocde_1"] == "INGENIERÍA Y TECNOLOGÍA") & (df_proyectos["año"] == 2024)])

# #humanidades del 2023
# humanidades_2023 = len(df_proyectos[(df_proyectos["ocde_1"] == "HUMANIDADES") & (df_proyectos["año"] == 2023)])
# humanidades_2024 = len(df_proyectos[(df_proyectos["ocde_1"] == "HUMANIDADES") & (df_proyectos["año"] == 2024)])

# #medicina y ciencias de la salud del 2023
# medicina_salud_2023 = len(df_proyectos[(df_proyectos["ocde_1"] == "MEDICINA Y CIENCIAS DE LA SALUD") & (df_proyectos["año"] == 2023)])
# medicina_salud_2024 = len(df_proyectos[(df_proyectos["ocde_1"] == "MEDICINA Y CIENCIAS DE LA SALUD") & (df_proyectos["año"] == 2024)])


class State(rx.State):
    """The app state."""

    proyectos: list[Proyectos] = []
    investigadores: list[Investigador] = []
    publicaciones: list[Publicaciones] = []
    grid_data: list[dict] = []   
    grid_data2: list[dict] = []

    search_value: str = ""
    search_value_card: str = ""
    sort_value: str = ""
    sort_reverse: bool = False
    search_term: str = ""
    filtered_count: int = 0
    filtered_year: list = []
    filtered_count_pub: int = 0

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

    #20/01/2025
    @rx.var
    def filtered_investigators(self) -> list[Investigador]:
        term = self.search_term.lower().strip()
        if term:
            filtered = [
                inv for inv in self.investigadores
                if (term in str(inv.id))
                or (term in inv.name.lower())
                # or (term in inv.titulo.lower())
                # or (term in inv.programa.lower())
            ]
        else:
            filtered = self.investigadores
        # if self.selected_areas:
        #     filtered = [inv for inv in filtered if inv.programa in self.selected_areas]
        return filtered
    
    #25/01/2025
    @rx.event
    def load_grid_data(self):
        if self.current_investigator:
            df_proyectos = pd.read_csv(proyectos_csv, encoding="utf-8-sig")
            df_publicaciones = pd.read_csv(publicaciones_csv, encoding="utf-8-sig")
            # Filter your dataframe based on current_investigator
            filtered_data = df_proyectos[df_proyectos["rut_ir"] == self.current_investigator.rut_ir]

            filtered_pub = df_publicaciones[df_publicaciones["rut_ir"] == self.current_investigator.rut_ir]

            #mostrar el año de cada proyecto filtrado
            filtered_year = df_proyectos[df_proyectos["rut_ir"] == self.current_investigator.rut_ir]["año"]

            self.grid_data = filtered_data.to_dict("records")
            self.grid_data2 = filtered_pub.to_dict("records")
            self.filtered_count = int(len(filtered_data))
            self.filtered_year = filtered_year.to_list()
            self.filtered_count_pub = int(len(filtered_pub))
                
    
    def set_search_term(self, term: str):
        """Actualiza la búsqueda."""
        self.search_term = term

    @rx.var(cache=False)
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
        self.current_investigator = inv

    @rx.var
    def current_investigator_is_none(self) -> bool:
        return self.current_investigator is None
    
    #Cargar academicas
    def load_academicas(self):
        # df = pd.read_csv(academicas_csv, encoding="ISO-8859-1")
        df = pd.read_csv(academicas_csv, delimiter="," ,encoding="ISO-8859-1")
        df = df.replace("", None)
        df["id"] = pd.to_numeric(df["id"], errors="coerce")  # Convierte números y pone NaN en errores
        df = df.dropna(subset=["id"])  # Elimina filas con NaN en "id"
        df["id"] = df["id"].astype(int)
        df["orcid"] = df["orcid"].fillna("")
        df["grado_mayor"] = df["grado_mayor"].astype(str)
        # df["grado_mayor"] = df["grado_mayor"].fillna("Investigadora")
        df["grado_mayor"] = df["grado_mayor"].replace("nan", "INVESTIGADORA")
        df["grado_mayor"] = df["grado_mayor"].replace("", "INVESTIGADORA")
        # df["grado_mayor"] = df["grado_mayor"].fillna("")
        # df["unidad_contrato"] = df["unidad_contrato"].fillna("")
        # df["ocde_2"] = df["ocde_2"].astype(str).apply(lambda x: " ,".join(x.split("#")) if x and x != "nan" else [])
        # df["ocde_2"] = df["ocde_2"].astype(str).apply(lambda x: x.split("#") if x and x != "nan" else [])
        df["ocde_2"] = df["ocde_2"].astype(str).apply(lambda x: ", ".join(x.split("#")) if x and x != "nan" else "")

        self.investigadores = [Investigador(**row.to_dict()) for _, row in df.iterrows()]

        # self.investigadores = [Investigador(**row.to_dict()) for _, row in df.iterrows()]
        self.total_investigadores = len(self.investigadores)
        # self.all_areas = df["programa"].dropna().unique().tolist()

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
        if self.search_value:
            search_value = self.search_value.lower()
            proyectos = [
                proyecto
                for proyecto in proyectos
                if any(
                    search_value in str(getattr(proyecto, attr)).lower()
                    for attr in [
                        "codigo", "titulo", "año", "disciplina",
                        "tipo_proyecto", "investigador_responsable",
                        "co_investigador", "unidad",
                    ]
                )
            ]
        return proyectos #12/12/2024
    
    @rx.var
    def filtered_sorted_pub(self) -> list[Publicaciones]:
        publicaciones = self.publicaciones
        if self.search_value:
            search_value = self.search_value.lower()
            publicaciones = [
                publicacion
                for publicacion in publicaciones
                if any(
                    search_value in str(getattr(publicacion, attr)).lower()
                    for attr in [
                        "año", "titulo", "revista", "cuartil",
                        "autor", "wos_id", "liderado", "url",
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

    #carga de proyectos
    def load_entries(self):
        if self.current_investigator is None:
            print("Error: self.current_investigator es None. No se pueden cargar proyectos.")
            return  # Salir de la función si no hay investigador seleccionado
        # if self.current_investigator is None:
        #     return
        df = pd.read_csv(proyectos_csv, encoding="utf-8-sig")
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
        # df["ocde_2"] = df["ocde_2"].fillna("SIN INFO")
        df["ocde_1"] = df["ocde_1"].fillna("Sin Info")
        # df["rol"] = df["rol"].astype(str).str.replace(";", "", regex=False).str.strip()
        # df["rol"] = df["rol"].replace("", "Sin rol")
        df["rol"] = df["rol"].fillna("Sin Info")
        # df["año"] = df["año"].astype(int)
        df["año"] = pd.to_numeric(df["año"], errors="coerce")  # fuerza a NaN si no es número
        df["año"] = df["año"].fillna(0).astype(int)
        self.proyectos = [Proyectos(**row) for _, row in df.iterrows()]
        self.total_items = len(self.proyectos)

    #carga de publicaciones
    def load_entries_pub(self):
        if self.current_investigator is None:
            print("Error: self.current_investigator es None. No se pueden cargar publicaciones.")
            return  # Salir de la función si no hay investigador seleccionado

        df = pd.read_csv(publicaciones_csv, encoding="utf-8-sig")
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

  
    # def load_grid_data(self):
    #     if self.current_investigator:
    #         # Filter your dataframe based on current_investigator
    #         filtered_data = df_proyectos[df_proyectos["rut_ir"] == self.current_investigator.rut_ir]
    #         self.grid_data = filtered_data.to_dict("records")