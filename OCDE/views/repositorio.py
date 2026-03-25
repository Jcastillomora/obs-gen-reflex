import reflex as rx
from ..backend.backend import State


def _doc_row(item: dict) -> rx.Component:
    return rx.vstack(
        rx.heading(item["heading_text"], weight="light", class_name="text-indigo-600"),
        rx.text(item["body_text"], class_name="text-indigo-400"),
        rx.link(
            rx.button("Descargar"),
            href=item["download_url"],
            is_external=True,
            download=True,
        ),
        rx.separator(class_name="bg-gray-300 my-2"),
        spacing="2",
        width="100%",
    )


def contenido_reportes(items) -> rx.Component:
    return rx.flex(
        rx.foreach(items, _doc_row),
        spacing="2",
        flex_direction="column",
        class_name="w-full",
    )


def repo_menu() -> rx.Component:
    return rx.accordion.root(
        rx.accordion.item(
            header=rx.text.kbd("Reportes", size="7", class_name="text-indigo-600"),
            content=contenido_reportes(State.reportes_items),
            value="item1",
            class_name="bg-white",
            color_scheme="indigo",
        ),
        rx.accordion.item(
            header=rx.text.kbd("Documentos", size="7", class_name="text-indigo-600"),
            content=contenido_reportes(State.documentos_items),
            value="item2",
            class_name="bg-white",
            color_scheme="indigo",
        ),
        collapsible=True,
        default_value="item2",
        type="multiple",
        variant="surface",
        color_scheme="indigo",
        class_name="w-full",
        show_dividers=True,
    )
