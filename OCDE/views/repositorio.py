import reflex as rx
from typing import List, Dict

def repo_menu() -> rx.Component:
    return rx.accordion.root(
    rx.accordion.item(
        header=rx.heading("Reportes"),
        content=reporte_componente,
        value="item1",
    ),
    rx.accordion.item(
        header=rx.heading("Documentos"),
        content=documentos_componente,
        value="item2",
    ),
    collapsible=True,
    default_value="item2",
    width="100%",
    type="multiple",
    variant="surface",
)

def contenido_reportes(reportes: List[Dict[str, str]]) -> rx.Component:
    """
    Espera una lista de diccionarios, donde cada diccionario tenga:
    {
      "heading_text": <str>,
      "body_text": <str>,
      "download_url": <str>
    }
    """
    secciones = []
    for reporte in reportes:
        secciones.extend(
            [
                rx.heading(reporte["heading_text"], weight="light"),
                rx.text(reporte["body_text"]),
                rx.link(
                    rx.button("Descargar", class_name="w-full sm:w-auto"),
                    href=reporte["download_url"],
                    is_external=True,
                    download=True,
                ),
                rx.separator(),
            ]
        )

    return rx.flex(
        *secciones,  # Expandimos la lista de componentes
        spacing="2",
        flex_direction="column",
        width="100%",
    )

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

reporte_componente = contenido_reportes(reportes_data)

documentos_componente = contenido_reportes(documentos_data)