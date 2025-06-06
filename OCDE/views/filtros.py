import reflex as rx
from ..backend.backend import State

# Chips y demás componentes
chip_props = {
    "radius": "full",
    "variant": "surface",
    "size": "3",
    "cursor": "pointer",
    "style": {"_hover": {"opacity": 0.75}},
}

def selected_area_chip(area: str) -> rx.Component:
    return rx.badge(
        area,
        rx.icon("circle-x", size=18),
        color_scheme="green",
        **chip_props,
        on_click=State.remove_area(area),
    )

def unselected_area_chip(area: str) -> rx.Component:
    return rx.cond(
        State.selected_areas.contains(area),
        rx.fragment(),
        rx.badge(
            area,
            rx.icon("circle-plus", size=18),
            color_scheme="gray",
            **chip_props,
            on_click=State.add_area(area),
        ),
    )

def areas_selector() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading(
                "Filtrar por Área"
                + f" ({State.selected_areas.length()})",
                size="4",
            ),
            rx.hstack(
                rx.button(
                    rx.icon("plus", size=16),
                    "Todas",
                    variant="soft",
                    size="2",
                    on_click=State.select_all_areas,
                    color_scheme="green",
                    cursor="pointer",
                ),
                rx.button(
                    rx.icon("trash", size=16),
                    "Limpiar",
                    variant="soft",
                    size="2",
                    on_click=State.clear_areas,
                    color_scheme="tomato",
                    cursor="pointer",
                ),
                spacing="2",
            ),
            justify="between",
            width="100%",
        ),
        rx.hstack(
            rx.foreach(State.selected_areas, selected_area_chip),
            wrap="wrap",
            spacing="2",
            justify_content="start",
        ),
        rx.divider(),
        rx.hstack(
            rx.foreach(State.all_areas, unselected_area_chip),
            wrap="wrap",
            spacing="2",
            justify_content="start",
        ),
        spacing="4",
        align_items="center",
        width="100%",
        class_name="bg-transparent shadow-lg p-10",
    )