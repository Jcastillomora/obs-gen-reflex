import reflex as rx
from ..backend.backend import State, Proyectos, Publicaciones
# from ..backend.data_items import teams_dict, position_dict
from ..backend.data_items import años_dict, disciplinas_dict, unidades_dict


def _header_cell(text: str, icon: str) -> rx.Component:
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(text, size="3"),
            align="center",
            spacing="2",
            class_name="text-indigo-900 font-semibold",
        ),
    )


def _show_player(proyectos: Proyectos, index: int) -> rx.Component:

    return rx.table.row(
        rx.table.row_header_cell(proyectos.codigo),
        rx.table.cell(proyectos.titulo),
        rx.table.cell(proyectos.año),
        rx.table.cell(proyectos.ocde_2),
        rx.table.cell(proyectos.tipo_proyecto),
        rx.table.cell(proyectos.rol),
        align="center",
        size="2",
        class_name="bg-white text-indigo-900 text-sm",
    )


def _show_pub(publicaciones: Publicaciones, index: int) -> rx.Component:

    return rx.table.row(
        rx.table.row_header_cell(publicaciones.año),
        rx.table.cell(publicaciones.titulo),
        rx.table.cell(publicaciones.revista),
        rx.table.cell(rx.button(
            "publicación", 
            size="1",
            radius="full",
            on_click=rx.redirect(publicaciones.url, is_external=True),
            )
        ),
        rx.table.cell(
            rx.vstack(
                rx.script(
                    "_altmetric_embed_init();"
                ),
                rx.html(
                    f'<div class="altmetric-embed" data-badge-popover="top" data-badge-type="2" data-hide-no-mentions="true" data-doi="{publicaciones.doi}"></div>'
                )
            ),        
        ),
        align="center",
        size="2",
        class_name="bg-white text-indigo-900 text-sm",
    )


def _pagination_view() -> rx.Component:
    """Paginación para PROYECTOS"""
    return (
        rx.hstack(
            rx.text(
                "Página ",
                State.page_number,
                f" de {State.total_pages}",
                justify="end",
                class_name="text-gray-700",
            ),
            rx.hstack(
                rx.icon_button(
                    rx.icon("chevrons-left", size=18),
                    on_click=State.first_page,
                    opacity=rx.cond(State.page_number == 1, 0.6, 1),
                    color_scheme=rx.cond(State.page_number == 1, "gray", "accent"),
                    variant="solid",
                ),
                rx.icon_button(
                    rx.icon("chevron-left", size=18),
                    on_click=State.prev_page,
                    opacity=rx.cond(State.page_number == 1, 0.6, 1),
                    color_scheme=rx.cond(State.page_number == 1, "gray", "accent"),
                    variant="solid",
                ),
                rx.icon_button(
                    rx.icon("chevron-right", size=18),
                    on_click=State.next_page,
                    opacity=rx.cond(State.page_number == State.total_pages, 0.6, 1),
                    color_scheme=rx.cond(
                        State.page_number == State.total_pages, "gray", "accent"
                    ),
                    variant="solid",
                ),
                rx.icon_button(
                    rx.icon("chevrons-right", size=18),
                    on_click=State.last_page,
                    opacity=rx.cond(State.page_number == State.total_pages, 0.6, 1),
                    color_scheme=rx.cond(
                        State.page_number == State.total_pages, "gray", "accent"
                    ),
                    variant="solid",
                ),
                align="center",
                spacing="2",
                justify="end",
            ),
            spacing="5",
            margin_top="1em",
            align="center",
            width="100%",
            justify="end",
        ),
    )


def _pagination_view_pub() -> rx.Component:
    """Paginación para PUBLICACIONES - usa variables separadas"""
    return (
        rx.hstack(
            rx.text(
                "Página ",
                State.page_number_pub,
                f" de {State.total_pages_pub}",
                justify="end",
                class_name="text-gray-700",
            ),
            rx.hstack(
                rx.icon_button(
                    rx.icon("chevrons-left", size=18),
                    on_click=State.first_page_pub,
                    opacity=rx.cond(State.page_number_pub == 1, 0.6, 1),
                    color_scheme=rx.cond(State.page_number_pub == 1, "gray", "accent"),
                    variant="solid",
                ),
                rx.icon_button(
                    rx.icon("chevron-left", size=18),
                    on_click=State.prev_page_pub,
                    opacity=rx.cond(State.page_number_pub == 1, 0.6, 1),
                    color_scheme=rx.cond(State.page_number_pub == 1, "gray", "accent"),
                    variant="solid",
                ),
                rx.icon_button(
                    rx.icon("chevron-right", size=18),
                    on_click=State.next_page_pub,
                    opacity=rx.cond(State.page_number_pub == State.total_pages_pub, 0.6, 1),
                    color_scheme=rx.cond(
                        State.page_number_pub == State.total_pages_pub, "gray", "accent"
                    ),
                    variant="solid",
                ),
                rx.icon_button(
                    rx.icon("chevrons-right", size=18),
                    on_click=State.last_page_pub,
                    opacity=rx.cond(State.page_number_pub == State.total_pages_pub, 0.6, 1),
                    color_scheme=rx.cond(
                        State.page_number_pub == State.total_pages_pub, "gray", "accent"
                    ),
                    variant="solid",
                ),
                align="center",
                spacing="2",
                justify="end",
            ),
            spacing="5",
            margin_top="1em",
            align="center",
            width="100%",
            justify="end",
        ),
    )


class EventArgState(rx.State):
    form_data: dict = {}

    @rx.event
    def handle_submit(self, form_data: dict):
        """Handle the form submit."""
        self.form_data = form_data

#Tabla de proyectos
def main_table() -> rx.Component:
    return rx.fragment(
        # rx.flex(
        #     rx.input(
        #         rx.input.slot(rx.icon("search")),
        #         rx.input.slot(
        #             rx.icon("x"),
        #             justify="end",
        #             cursor="pointer",
        #             on_click=State.setvar("search_value_proy", ""),
        #             display=rx.cond(State.search_value_proy, "flex", "none"),
        #         ),
        #         value=State.search_value_proy,
        #         placeholder="Buscar aquí...",
        #         size="3",
        #         max_width="250px",
        #         width="100%",
        #         variant="surface",
        #         color_scheme="gray",
        #         on_change=State.set_search_value_proy,
        #     ),
        #     align="center",
        #     justify="end",
        #     spacing="3",
        #     wrap="wrap",
        #     width="100%",
        #     padding_bottom="1em",
        # ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("Código", "text-search"),
                    _header_cell("Título", "notebook-pen"),
                    _header_cell("Año", "calendar"),
                    _header_cell("Disciplina", "user-round-search"),
                    _header_cell("Tipo proyecto", "filter"),
                    _header_cell("Rol", "building"),
                ),
                class_name="w-full bg-indigo-400",
            ),
            rx.table.body(
                rx.foreach(
                    State.get_current_page,
                    # State.filtered_proyectos,
                    lambda proyectos, index: _show_player(proyectos, index),
                )
            ),
            variant="surface",
            size="2",
            width="100%",
        ),
        _pagination_view(),
    )

#Tabla de publicaciones
def pub_table() -> rx.Component:
    return rx.fragment(
        # rx.flex(
        #     rx.input(
        #         rx.input.slot(rx.icon("search")),
        #         rx.input.slot(
        #             rx.icon("x"),
        #             justify="end",
        #             cursor="pointer",
        #             on_click=State.setvar("search_value_pub", ""),
        #             display=rx.cond(State.search_value_pub, "flex", "none"),
        #         ),
        #         value=State.search_value_pub,
        #         placeholder="Buscar aquí...",
        #         size="3",
        #         max_width="250px",
        #         width="100%",
        #         variant="surface",
        #         color_scheme="indigo",
        #         on_change=State.set_search_value_pub,
        #     ),
        #     align="center",
        #     justify="end",
        #     spacing="3",
        #     wrap="wrap",
        #     width="100%",
        #     padding_bottom="1em",
        # ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("Año", "calendar"),
                    _header_cell("Título", "notebook-pen"),
                    _header_cell("Revista", "book-open-text"),
                    _header_cell("Link", "external-link"),
                    _header_cell("Altmetric", "badge"),
                ),
                class_name="w-full bg-indigo-400",
            ),
            rx.table.body(
                rx.foreach(
                    State.get_current_page_pub,
                    # State.filtered_proyectos,
                    lambda publicaciones, index: _show_pub(publicaciones, index),
                )
            ),
            variant="surface",
            size="2",
            class_name="w-full",
        ),
        _pagination_view_pub(),  # <-- CAMBIADO: usar paginación específica para publicaciones
        
    )