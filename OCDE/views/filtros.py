import reflex as rx
from ..backend.backend import State
from ..components.ai_search import simple_ai_search_replace


# Chips y demás componentes
chip_props = {
    "radius": "full",
    "variant": "surface",
    "size": "3",
    "cursor": "pointer",
    # "style": {"_hover": {"opacity": 0.75}},
}

def selected_area_chip(area: str) -> rx.Component:
    return rx.badge(
        area,
        rx.icon("circle-x", size=18),
        color_scheme="indigo",
        **chip_props,
        on_click=State.remove_area(area),
        class_name="bg-white",       
    )
    

def unselected_area_chip(area: str) -> rx.Component:
    return rx.cond(
        State.selected_areas.contains(area),
        rx.fragment(),
        rx.badge(
            area,
            rx.icon("circle-plus", size=18),
            color_scheme="indigo",
            **chip_props,
            on_click=State.add_area(area),
        ),
    )

def areas_selector() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            # rx.heading(
            #     "Filtrar por Disciplina OCDE nivel 2"
            #     + f" ({State.selected_areas.length()})",
            #     class_name="text-sm sm:text-lg text-gray-700 font-semibold p-2",
            # ),
            rx.hstack(
                # rx.button(
                #     rx.icon("plus", size=16),
                #     "Todas",
                #     variant="soft",
                #     size="2",
                #     on_click=State.select_all_areas,
                #     color_scheme="green",
                #     cursor="pointer",
                # ),
                # rx.button(
                #     rx.icon("trash", size=16),
                #     "Limpiar",
                #     variant="soft",
                #     size="2",
                #     on_click=State.clear_areas,
                #     color_scheme="tomato",
                #     cursor="pointer",
                # ),
                spacing="2",
                class_name="px-2",
            ),
            justify="between",
            width="100%",
        ),
        rx.callout(
            "Pronto actualizaremos publicaciones, proyectos y perfiles de investigadoras.",
            icon="info",
            color_scheme="tomato",
            # role="alert",
        ),
        rx.text(
            """Este espacio reúne a las investigadoras de la Universidad de La Frontera, destacando su trayectoria académica y científica a través de sus proyectos entre 2018-2024, publicaciones WoS y Scopus entre 2018-2022.
            El buscador permite explorar y filtrar perfiles según líneas de investigación, organizadas por disciplina OCDE nivel 2, facilitando la búsqueda de experticia específica en diversas áreas del conocimiento.
            """,
            class_name="text-sm sm:text-lg text-indigo-900 p-2",
        ),
        rx.vstack(
            rx.text("Búsqueda de Investigadoras por nombre", class_name="text-sm sm:text-lg text-gray-700 font-semibold"),
            rx.input(
                rx.input.slot(rx.icon("search")),
                rx.input.slot(
                    rx.icon("x", on_click=lambda: State.set_search_term("")),
                    justify="end",
                    cursor="pointer",
                ),
                value=State.search_term,
                placeholder="Buscar Investigadoras",
                size="2",
                max_width="450px",
                width="100%",
                variant="classic",
                color_scheme="indigo",
                on_change=lambda val: State.set_search_term(val),
                    ),
            spacing="2",
            width="100%",
        ),

        # nuevo
        # rx.hstack(
        #     rx.text("Búsqueda por línea de investigación según disciplina OCDE nivel 2", class_name="text-sm sm:text-lg text-gray-700 font-semibold"),
        #     rx.select(
        #         items=State.sorted_areas,
        #         on_change=lambda e: State.set_selected_area_temp(e),
        #         placeholder="Selecciona un área",
        #         size="2",
        #         color_scheme="indigo",
        #         variant="classic",
        #         style={"minWidth": "300px"},
        #         class_name="font-semibold",
        #     ),
        #     rx.button(
        #         rx.icon("plus", size=16),
        #         "Agregar área",
        #         on_click=State.add_selected_area,
        #         variant="soft",
        #         size="2",
        #         color_scheme="indigo",
        #     ),
        #     rx.button(
        #         rx.icon("trash", size=16),
        #         "Limpiar área",
        #         variant="soft",
        #         size="2",
        #         on_click=State.clear_areas,
        #         color_scheme="tomato",
        #         cursor="pointer",
        #     ),
        #     spacing="2",
        #     reset_on_submit=True,
        #     class_name="w-full",
        # ),
        rx.box(
            # Primera fila: texto
            rx.text(
                "Búsqueda por línea de investigación según disciplina OCDE nivel 2",
                class_name="text-sm sm:text-lg text-gray-700 font-semibold mb-2 lg:mb-0",
            ),
            # Segunda fila: controles
            rx.flex(
                rx.select(
                    items=State.sorted_areas,
                    on_change=lambda e: State.set_selected_area_temp(e),
                    placeholder="Selecciona un área",
                    size="2",
                    color_scheme="indigo",
                    variant="classic",
                    class_name="font-semibold flex-1 min-w-0",
                ),
                rx.button(
                    rx.icon("plus", size=16),
                    rx.text("Agregar", class_name="hidden sm:inline"),
                    on_click=State.add_selected_area,
                    variant="soft",
                    size="2",
                    color_scheme="indigo",
                ),
                rx.button(
                    rx.icon("trash", size=16),
                    rx.text("Limpiar", class_name="hidden sm:inline"),
                    variant="soft",
                    size="2",
                    on_click=State.clear_areas,
                    color_scheme="tomato",
                    cursor="pointer",
                ),
                spacing="2",
                align="center",
                class_name="w-full",
            ),
            class_name="flex flex-col lg:flex-row lg:items-center lg:gap-4 w-full",
        ),
        rx.hstack(
            rx.divider(),
            rx.foreach(State.selected_areas, selected_area_chip),
            wrap="wrap",
            spacing="2",
            justify_content="start",
        ),

        rx.vstack(
            rx.text("Búsqueda Avanzada con IA", class_name="text-sm sm:text-lg text-gray-700 font-semibold"),
            simple_ai_search_replace(),
            spacing="2",
            width="100%",
        ),

        # rx.hstack(
        #     rx.divider(),
        #     rx.foreach(State.selected_areas, selected_area_chip),
        #     wrap="wrap",
        #     spacing="2",
        #     justify_content="start",
        # ),
        rx.divider(),
        # rx.hstack(
        #     rx.foreach(State.all_areas, unselected_area_chip),
        #     wrap="wrap",
        #     spacing="2",
        #     justify_content="start",
        # ),
        # spacing="4",
        align_items="center",
        width="100%",
        class_name="bg-white shadow-lg lg:px-50 p-5 py-5",
    )