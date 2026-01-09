import reflex as rx
from typing import List, Dict

reportes_data = [
    {
        "heading_text": "Reporte General 2024",
        "body_text": "Contenido de la primera sección",
        "download_url": "/#",
    },
    {
        "heading_text": "Reporte Regional 2025",
        "body_text": "Contenido de la segunda sección",
        "download_url": "/#",
    },
    {
        "heading_text": "Reporte Especial 2026",
        "body_text": "Contenido de la tercera sección",
        "download_url": "/#",
    },
]

documentos_data = [
    {
        "heading_text": "Alianza de mujeres en la academia",
        "body_text": "Universidad de los Andes, 2024",
        "download_url": "/alianza_mujeres.pdf",
    },
    {
        "heading_text": "Encuesta mujeres en la academia (EMA)",
        "body_text": "Universidad Mayor, 2025",
        "download_url": "/encuesta_EMA.pdf",
    },
]


def contenido_reportes(reportes: list[dict[str, str]]) -> rx.Component:
    secciones = []
    for reporte in reportes:
        secciones.extend(
            [
                rx.heading(reporte["heading_text"], weight="light", class_name="text-indigo-600"),
                rx.text(reporte["body_text"], class_name="text-indigo-400"),
                rx.link(
                    rx.button("Descargar"),
                    href=reporte["download_url"],
                    is_external=True,
                    download=True,
                ),
                rx.separator(class_name="bg-gray-300 my-2"),
            ]
        )
    return rx.flex(
        *secciones,
        spacing="2",
        flex_direction="column",
        class_name="w-full",
    )


def repo_menu() -> rx.Component:
    return rx.accordion.root(
        rx.accordion.item(
            header=rx.text.kbd("Reportes", size="7", class_name="text-indigo-600"),
            content=contenido_reportes(reportes_data),
            value="item1",
            class_name="bg-white",
            color_scheme="indigo",
        ),
        rx.accordion.item(
            header=rx.text.kbd("Documentos", size="7", class_name="text-indigo-600"),
            content=contenido_reportes(documentos_data),
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