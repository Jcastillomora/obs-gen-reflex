import reflex as rx
from ..backend.backend import State, Proyectos, Publicaciones, Libros
# from ..backend.data_items import teams_dict, position_dict
from ..backend.data_items import años_dict, disciplinas_dict, unidades_dict


def _sort_button(label: str, on_click, is_desc: rx.Var) -> rx.Component:
    """Botón de toggle de orden ascendente/descendente."""
    return rx.button(
        rx.hstack(
            rx.icon(
                rx.cond(is_desc, "arrow-down-z-a", "arrow-up-z-a"),
                size=15,
            ),
            rx.text(rx.cond(is_desc, f"{label}: Z→A / reciente", f"{label}: A→Z / antiguo"), size="1"),
            spacing="1",
            align="center",
        ),
        on_click=on_click,
        size="1",
        variant="soft",
        color_scheme="indigo",
        class_name="mb-2",
    )


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


def _periodo(p: Proyectos) -> rx.Component:
    """Muestra 'a_inicio – a_fin' cuando están disponibles, si no '—'."""
    return rx.cond(
        p.a_inicio != "",
        rx.text(p.a_inicio + rx.cond(p.a_fin != "", " – " + p.a_fin, "")),
        rx.text("—", class_name="text-gray-400"),
    )


def _show_player(proyectos: Proyectos, index: int) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(proyectos.titulo),
        rx.table.cell(_periodo(proyectos)),
        rx.table.cell(proyectos.rol),
        rx.table.cell(
            rx.cond(
                proyectos.fuente != "",
                rx.text(proyectos.fuente),
                rx.text("—", class_name="text-gray-400"),
            )
        ),
        align="center",
        size="2",
        class_name="bg-white text-indigo-900 text-sm",
    )


def _show_pub(publicaciones: Publicaciones, index: int) -> rx.Component:

    return rx.table.row(
        rx.table.row_header_cell(publicaciones.año),
        rx.table.cell(publicaciones.titulo),
        rx.table.cell(publicaciones.revista),
        rx.table.cell(publicaciones.indexacion),
        # rx.table.cell(rx.button(
        #     "publicación", 
        #     size="1",
        #     radius="full",
        #     on_click=rx.redirect(publicaciones.url, is_external=True),
        #     )
        # ),
        # rx.table.cell(
        #     rx.vstack(
        #         rx.script(
        #             "_altmetric_embed_init();"
        #         ),
        #         rx.html(
        #             f'<div class="altmetric-embed" data-badge-popover="top" data-badge-type="2" data-hide-no-mentions="true" data-doi="{publicaciones.doi}"></div>'
        #         )
        #     ),        
        # ),
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


def _show_libro(libro: Libros, index: int) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(libro.titulo),
        rx.table.cell(libro.año),
        rx.table.cell(libro.editorial),
        rx.table.cell(libro.isbn),
        rx.table.cell(libro.autores),
        align="center",
        size="2",
        class_name="bg-white text-indigo-900 text-sm",
    )


def _pagination_view_libros() -> rx.Component:
    """Paginación para LIBROS"""
    return (
        rx.hstack(
            rx.text(
                "Página ",
                State.page_number_libros,
                f" de {State.total_pages_libros}",
                justify="end",
                class_name="text-gray-700",
            ),
            rx.hstack(
                rx.icon_button(
                    rx.icon("chevrons-left", size=18),
                    on_click=State.first_page_libros,
                    opacity=rx.cond(State.page_number_libros == 1, 0.6, 1),
                    color_scheme=rx.cond(State.page_number_libros == 1, "gray", "accent"),
                    variant="solid",
                ),
                rx.icon_button(
                    rx.icon("chevron-left", size=18),
                    on_click=State.prev_page_libros,
                    opacity=rx.cond(State.page_number_libros == 1, 0.6, 1),
                    color_scheme=rx.cond(State.page_number_libros == 1, "gray", "accent"),
                    variant="solid",
                ),
                rx.icon_button(
                    rx.icon("chevron-right", size=18),
                    on_click=State.next_page_libros,
                    opacity=rx.cond(State.page_number_libros == State.total_pages_libros, 0.6, 1),
                    color_scheme=rx.cond(
                        State.page_number_libros == State.total_pages_libros, "gray", "accent"
                    ),
                    variant="solid",
                ),
                rx.icon_button(
                    rx.icon("chevrons-right", size=18),
                    on_click=State.last_page_libros,
                    opacity=rx.cond(State.page_number_libros == State.total_pages_libros, 0.6, 1),
                    color_scheme=rx.cond(
                        State.page_number_libros == State.total_pages_libros, "gray", "accent"
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


# Tabla de libros
def libros_table() -> rx.Component:
    return rx.fragment(
        _sort_button("Año", State.toggle_sort_libros, State.sort_reverse_libros),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("Título", "book-open"),
                    _header_cell("Año", "calendar"),
                    _header_cell("Editorial", "building-2"),
                    _header_cell("ISBN", "barcode"),
                    _header_cell("Autores", "users"),
                ),
                class_name="w-full bg-indigo-400",
            ),
            rx.table.body(
                rx.foreach(
                    State.get_current_page_libros,
                    lambda libro, index: _show_libro(libro, index),
                )
            ),
            variant="surface",
            size="2",
            class_name="w-full",
        ),
        _pagination_view_libros(),
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
        _sort_button("Año", State.toggle_sort, State.sort_reverse),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("Título", "notebook-pen"),
                    _header_cell("Período", "calendar-range"),
                    _header_cell("Rol", "building"),
                    _header_cell("Fuente", "landmark"),
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
        _sort_button("Año", State.toggle_sort_pub, State.sort_reverse_pub),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("Año", "calendar"),
                    _header_cell("Título", "notebook-pen"),
                    _header_cell("Revista", "book-open-text"),
                    _header_cell("Indexación", "database"),
                    # _header_cell("Link", "external-link"),
                    # _header_cell("Altmetric", "badge"),
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