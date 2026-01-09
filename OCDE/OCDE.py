from .backend.backend import State
from .views.navbar import navbar
from .views.table import main_table, pub_table
from .views.stats import stats_ui
from .views.footer import footer
from .views.searchbar import navbar_searchbar, navbar_searchbar_notsearch
from .views.repositorio import repo_menu
from .views.home import (
    huincha,
    contenido_home,
    superbanner,
    footer_inst,
    navbar_main,
    banner_generator,
)
from .views.carousel import carousel
from .views.filtros import areas_selector
from .components.chatbot import chatbot_assistant
import reflex as rx
from reflex.components.core.breakpoints import Breakpoints


# Página de inicio
@rx.page(route="/", title="Inicio")
def obs_inicio():
    return rx.vstack(
        huincha(),
        banner_generator("/banner_home.jpg"),
        navbar_main(),
        contenido_home(),
        # rx.flex(
        #     carousel(),
        #     class_name="w-full relative",
        # ),
        superbanner(),
        footer_inst(),
        spacing="0",
        align="stretch",
        class_name="w-full",
    )


# Página de indicadores
@rx.page(route="/obs_indicadores", title="Indicadores")
def obs_indicadores():
    return rx.vstack(
        huincha(),
        banner_generator("/banner_indicadores.png"),
        navbar_main(),
        rx.box(
            rx.desktop_only(
                rx.html(
                    """
                    <iframe
                        title='indicadores_ines_genero_v2'
                        src='https://app.powerbi.com/view?r=eyJrIjoiZjM2MGFmMzgtNzllMi00YjkyLWIxNjItMDIxNGZjMDZmZGExIiwidCI6ImZjZDlhYmQ4LWRmY2QtNGExYS1iNzE5LThhMTNhY2ZkNWVkOSIsImMiOjR9'
                        frameborder='0'
                        allowFullScreen='true'
                        width='800'
                        height='636'
                        style='aspect-ratio: 16/9; width: 100%;'
                    ></iframe>
                    """
                ),
                class_name="p-10",
            ),
            rx.mobile_and_tablet(
                rx.html(
                    """
                    <iframe
                        title='indicadores_ines_genero_v2'
                        src='https://app.powerbi.com/view?r=eyJrIjoiZjM2MGFmMzgtNzllMi00YjkyLWIxNjItMDIxNGZjMDZmZGExIiwidCI6ImZjZDlhYmQ4LWRmY2QtNGExYS1iNzE5LThhMTNhY2ZkNWVkOSIsImMiOjR9'
                        frameborder='0'
                        allowFullScreen='true'
                        style='aspect-ratio: 16/9; width: 100%;'
                    ></iframe>
                    """
                ),
            ),
            width="100%",
            class_name="sm:p-2 px-3 justify-center items-center",
            style={"overflowX": "hidden"},
        ),
        superbanner(),
        footer_inst(),
        spacing="0",
        class_name="w-full bg-white",
    )


# Página de indicadores
@rx.page(route="/obs_otros_indicadores", title="Otros Indicadores")
def obs_otros_indicadores():
    return rx.vstack(
        huincha(),
        banner_generator("/banner_indicadores.png"),
        navbar_main(),
        rx.box(
            rx.desktop_only(
                rx.html(
                    """
                    <iframe
                        title='indicadores_ines_genero_v2'
                        src='https://app.powerbi.com/view?r=eyJrIjoiM2U1MzJmZTItYzEyZC00ZjBiLTkwMDItODVjOTIwOGNmOWZjIiwidCI6ImZjZDlhYmQ4LWRmY2QtNGExYS1iNzE5LThhMTNhY2ZkNWVkOSIsImMiOjR9'
                        frameborder='0'
                        allowFullScreen='true'
                        width='800'
                        height='636'
                        style='aspect-ratio: 16/9; width: 100%;'
                    ></iframe>
                    """
                ),
                class_name="p-10",
            ),
            rx.mobile_and_tablet(
                rx.html(
                    """
                    <iframe
                        title='indicadores_ines_genero_v2'
                        src='https://app.powerbi.com/view?r=eyJrIjoiM2U1MzJmZTItYzEyZC00ZjBiLTkwMDItODVjOTIwOGNmOWZjIiwidCI6ImZjZDlhYmQ4LWRmY2QtNGExYS1iNzE5LThhMTNhY2ZkNWVkOSIsImMiOjR9'
                        frameborder='0'
                        allowFullScreen='true'
                        style='aspect-ratio: 16/9; width: 100%;'
                    ></iframe>
                    """
                ),
            ),
            width="100%",
            class_name="sm:p-2 px-3 justify-center items-center",
            style={"overflowX": "hidden"},
        ),
        superbanner(),
        footer_inst(),
        spacing="0",
        class_name="w-full bg-white",
    )


# Página de repositorio
@rx.page(route="/obs_repositorio", title="Repositorio")
def obs_repositorio():
    return rx.vstack(
        huincha(),
        banner_generator("/banner_repositorio.jpg"),
        navbar_main(),
        rx.vstack(
            rx.spacer(),
            rx.callout(
                "Pronto subiremos el primer reporte del Observatorio",
                icon="info",
                color_scheme="tomato",
                class_name="w-full text-center",
                # role="alert",
            ),
            chatbot_assistant(),
            repo_menu(),
            class_name="w-full bg-white sm:w-3/4 p-5",
            spacing="2",
        ),
        superbanner(),
        footer_inst(),
        spacing="0",
        align="center",
        class_name="w-full bg-white",
    )


# Página de contacto
@rx.page(route="/obs_contacto", title="Contacto")
def obs_contacto():
    return rx.vstack(
        huincha(),
        banner_generator("/banner_contacto.png"),
        navbar_main(),
        # rx.flex(
        #     contact_form(),
        #     class_name="p-10",
        # ),
        rx.desktop_only(
            rx.flex(
                rx.html(
                    """
                <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdxHZqMCyLNV9LOs5zO0P7Dzj4YTatTpMNpjEGNf62T8DhDuw/viewform?embedded=true" width="640" height="1325" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
                """,
                ),
                rx.html(
                    """
                <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdbf9MB2Urtx5eaViOJrsusbcDuFEyBKOIy_d2cIIt5_vdx4Q/viewform?embedded=true" width="640" height="1280" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
                """,
                ),
                spacing="1",
                class_name="p-10",
            ),
        ),
        rx.mobile_and_tablet(
            rx.flex(
                rx.html(
                    """
                <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdbf9MB2Urtx5eaViOJrsusbcDuFEyBKOIy_d2cIIt5_vdx4Q/viewform?embedded=true" width="300" height="1280" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
                """,
                ),
                rx.html(
                    """
                <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdxHZqMCyLNV9LOs5zO0P7Dzj4YTatTpMNpjEGNf62T8DhDuw/viewform?embedded=true" width="300" height="1325" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
                """,
                ),
                spacing="6",
                class_name="p-2",
                direction="column",
            ),
        ),
        superbanner(),
        footer_inst(),
        spacing="0",
        align="center",
        background_image="url('/bg_inv.jpg')",
        background_size="cover",
        background_repeat="no-repeat",
        background_position="center",
        class_name="w-full bg-white",
    )


# Página de investigadores
@rx.page(route="/investigadoras", on_load=State.load_academicas)
def academicas():
    return rx.vstack(
        huincha(),
        banner_generator("/banner_home.jpg"),
        navbar_main(),
        navbar_searchbar(),
        areas_selector(),
        # Mensaje de feedback de búsqueda
        rx.box(
            rx.text(
                State.search_message,
                size="3",
                class_name="text-gray-600 text-center p-4"
            ),
            width="100%",
            class_name="md:px-40 px-5"
        ),
        rx.flex(
            rx.cond(
                ~State.search_results_empty,
                rx.hstack(
                    rx.foreach(State.filtered_investigators, investigador_card),
                    wrap="wrap",
                    justify="center",
                ),
                rx.box(
                    rx.text(
                        "Intenta ajustar los filtros de búsqueda.",
                        size="2",
                        class_name="text-gray-500 text-center"
                    ),
                    class_name="py-8"
                )
            ),
            class_name="w-full md:px-40 p-5",
            flex="1",
            spacing="3",
        ),
        footer_inst(),
        spacing="0",
        align="stretch",
        # wrap="wrap",
        background_image="url('/bg_aca_.jpg')",
        # background_size="cover",
        class_name="w-full h-auto",
    )

def investigador_card(
    inv, on_load=[State.load_academicas, State.load_entries_pub, State.load_entries]
):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.flex(
                    rx.image(src="/icono_inv.png", alt="Icono investigadora"),
                    radius="full",
                ),
                rx.vstack(
                    rx.heading(
                        inv["name"],
                        size="4",
                        class_name="text-indigo-900",
                    ),
                    rx.text(
                        inv["grado_mayor"],
                        size="2",
                        weight="medium",
                        class_name="text-indigo-600",
                    ),
                    spacing="1",
                    width="100%",
                ),
                height="100%",
                spacing="4",
                align="center",
                width="100%",
            ),
            rx.hstack(
                rx.link(
                    rx.image(
                        src="/orcid_icon.png", alt="ORCID", width="24px", height="24px"
                    ),
                    href=rx.cond(
                        inv["orcid"],
                        inv["orcid"],
                        "#",
                    ),
                    is_external=True,
                ),
                rx.link(
                    rx.button(
                        rx.icon("circle-arrow-right", size=16),
                        "Contactar",
                        size="2",
                        variant="solid",
                        color_scheme="purple",
                    ),
                    href=rx.cond(
                        inv["id"],
                        f"/investigadora/{inv['id']}",
                        "#",
                    ),
                ),
                justify="center",
                width="100%",
                spacing="3",
            ),
            spacing="3",
        ),
        size="3",
        width="100%",
        max_width="21rem",
        class_name="p-5 md:m-5 shadow-lg",
    )


def _tabs_trigger(text: str, icon: str, value: str):
    return rx.tabs.trigger(
        rx.hstack(
            rx.icon(icon, size=24, class_name="text-indigo-900"),
            rx.heading(text, size="5", class_name="text-indigo-900"),
            spacing="2",
            align="center",
            width="100%",
        ),
        value=value,
    )

def adaptive_badge(item: rx.Var[str]) -> rx.Component:
    """A responsive badge that truncates long text and shows full content on hover."""
    return rx.el.div(
        rx.el.span(item.strip(), class_name="truncate"),
        rx.el.div(
            item.strip(),
            class_name="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-max max-w-xs p-2 text-sm bg-gray-900 text-white rounded-md shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10",
        ),
        class_name="group relative flex items-center bg-indigo-500 text-white text-sm font-medium px-3 py-1.5 rounded-full border border-violet-200 shadow-sm hover:bg-violet-400 transition-all cursor-default max-w-[200px] m-1",
    )

# Página perfil del investigador
@rx.page(
    route="/investigadora/[id]",
    on_load=[State.load_entries_pub, State.load_entries, State.load_grid_data],
)
def investigator_page():
    """Muestra el detalle del investigador según el índice en la URL."""
    return rx.vstack(
        huincha(),
        navbar_searchbar_notsearch(),
        rx.spacer(),
        rx.flex(
            rx.grid(
                rx.desktop_only(
                    rx.hstack(
                        rx.avatar(
                            size="9",
                            # fallback=State.current_investigator.name[0],
                            fallback=State.get_initials,
                            variant="solid",
                            radius="full",
                            color_scheme="iris",
                            # background_color="#a280f6",
                            class_name="text-white",
                        ),
                        rx.box(
                            rx.text(
                                f"{State.current_investigator.name}",
                                class_name="text-3xl font-bold text-white p-2",
                            ),
                            rx.text(
                                f"{State.current_investigator.grado_mayor}",
                                class_name="text-white text-lg font-extralight p-2 break-words whitespace-normal",
                            ),
                            rx.hstack(
                                # rx.link(
                                #     rx.image(src="/orcid_icon.png"),
                                #     href=rx.cond(
                                #         State.current_investigator.orcid,  # Condición
                                #         State.current_investigator.orcid,  # Valor si es verdadero
                                #         "#",                               # Valor si es falso
                                #     ),
                                #     is_disabled=rx.cond(
                                #         State.current_investigator.orcid,  # Condición
                                #         False,                            # Habilitar el enlace si hay ORCID
                                #         True,                             # Deshabilitar el enlace si no hay ORCID
                                #     ),
                                # ),
                                rx.hover_card.root(
                                    rx.hover_card.trigger(
                                        rx.link(
                                            rx.image(src="/orcid_icon.png"),
                                            href=rx.cond(
                                                State.current_investigator.orcid,
                                                State.current_investigator.orcid,
                                                "#",
                                            ),
                                            is_disabled=~State.current_investigator.orcid,
                                            # is_disabled=rx.cond(
                                            #     State.current_investigator.orcid,
                                            #     False,
                                            #     True,
                                            # ),
                                        ),
                                    ),
                                    rx.hover_card.content(
                                        rx.text(
                                            "ORCID: un identificador único y permanente que distingue a los investigadores y conecta sus publicaciones y proyectos."
                                            "Para más información, visita el sitio web de ORCID ",
                                            rx.link(
                                                "Click Aquí", href="https://orcid.org/"
                                            ),
                                            class_name="text-sm text-gray-700 p-2",
                                        ),
                                        class_name="bg-white p-2 rounded-lg shadow-lg max-w-xs",
                                    ),
                                ),
                                rx.link(
                                    rx.button(
                                        rx.icon("message-circle-more", size=16),
                                        State.current_investigator.email,
                                        size="2",
                                        width="100%",
                                        cursor="pointer",
                                        class_name=(
                                            "text-white rounded-full p-2.5 "
                                            "bg-gradient-to-r from-cyan-500 "
                                            "to-blue-500 hover:bg-gradient-to-bl "
                                            "font-medium rounded-lg text-sm text-center"
                                        ),
                                    ),
                                    href=f"mailto:{State.current_investigator.email}",
                                    # href=f"/investigador/{i}",
                                ),
                                align="center",
                                width="100%",
                                spacing="6",
                            ),
                            rx.box(
                                rx.text(
                                    "Disciplinas OCDE nivel 2",
                                    class_name="text-white p-2",
                                ),
                            ),
                            # rx.cond(
                            #     State.current_investigator.ocde_2,  # Si existe el campo
                            #     rx.grid(
                            #         rx.foreach(
                            #             State.current_investigator.ocde_2.split(", "),  # Divide los valores
                            #             lambda item: rx.badge(
                            #                 item.strip(),
                            #                 size="3",
                            #                 variant="solid",
                            #                 color_scheme="purple",
                            #                 high_contrast=True,
                            #                 class_name="truncate text-center text-xs max-w-[150px] whitespace-nowrap overflow-hidden text-ellipsis px-2"  # Margen entre badges
                            #             )
                            #         ),
                            #         columns=Breakpoints(initial="1", sm="2", md="3", lg="3", xl="3"),
                            #         spacing="2",
                            #         class_name="w-full py-5 text-xs text-center" # Margen superior
                            #     )
                            # ),
                            rx.cond(
                                State.current_investigator.ocde_2,
                                rx.flex(
                                    rx.foreach(
                                        State.current_investigator.ocde_2.split(","),
                                        adaptive_badge,
                                    ),
                                    wrap="wrap",
                                    spacing="3",
                                    class_name="w-full p-2",
                                ),
                                rx.box(
                                    rx.text(
                                        "No hay datos disponibles",
                                        class_name="text-white p-2",
                                    ),
                                ),
                            ),
                            spacing="4",
                            class_name="p-2",
                            width="100%",
                        ),
                        rx.spacer(),
                        rx.vstack(
                            rx.hstack(
                                rx.image(src="/total_pro.png"),
                                rx.spacer(),
                                rx.text("Proyectos: ", class_name="text-white text-xl"),
                                rx.text(
                                    f"{State.filtered_count}",
                                    class_name="text-white text-2xl font-semibold",
                                ),
                                class_name="items-center justify-center gap-2",
                            ),
                            rx.divider(size="4", class_name="w-3/4 bg-white"),
                            rx.hstack(
                                rx.image(src="/total_pub.png"),
                                rx.spacer(),
                                rx.text(
                                    "Publicaciones: ", class_name="text-white text-xl"
                                ),
                                rx.text(
                                    f"{State.filtered_count_pub}",
                                    class_name="text-white text-2xl font-semibold",
                                ),
                                class_name="items-center justify-center gap-2",
                            ),
                            width="100%",
                            spacing="5",
                            class_name="pl-80",
                            # align="end",
                            # class_name="px-80"
                        ),
                        width="100%",
                        spacing="1",
                        class_name="px-10",
                    ),
                    spacing="4",
                    background_image="url('/bg_perfil.png')",
                    border_radius="10px",
                    background_size="cover",
                    background_repeat="no-repeat",
                    background_position="right",
                    class_name="w-full p-10 text-left",
                ),
                rx.mobile_only(
                    rx.vstack(
                        rx.avatar(
                            size="9",
                            # color_scheme="crimson",
                            fallback=State.get_initials,
                            radius="full",
                            variant="solid",
                            color_scheme="iris",
                            # background_color="#a280f6",
                            class_name="text-white",
                        ),
                        rx.box(
                            rx.text(
                                f"{State.current_investigator.name}",
                                class_name="text-2xl font-semibold text-white p-1",
                            ),
                            rx.text(
                                f"{State.current_investigator.grado_mayor}",
                                class_name="text-white p-1",
                            ),
                            # rx.cond(
                            #     State.current_investigator.magister is None,
                            #     rx.text(f"{State.current_investigator.magister}", class_name="text-indigo-900 italic")
                            # ),
                            width="100%",
                        ),
                        rx.hstack(
                            # rx.image(src="/orcid_icon.png"),
                            rx.link(
                                rx.image(src="/orcid_icon.png"),
                                href=rx.cond(
                                    State.current_investigator.orcid,
                                    State.current_investigator.orcid,
                                    "#",
                                ),
                                is_disabled=rx.cond(
                                    State.current_investigator.orcid,
                                    False,
                                    True,
                                ),
                            ),
                            rx.link(
                                rx.button(
                                    rx.icon("message-circle-more", size=16),
                                    "Contactar",
                                    size="2",
                                    variant="solid",
                                    color_scheme="blue",
                                    width="100%",
                                    cursor="pointer",
                                    class_name=(
                                        "text-white rounded-full p-2.5 "
                                        "bg-gradient-to-r from-cyan-500 "
                                        "to-blue-500 hover:bg-gradient-to-bl "
                                        "font-medium rounded-lg text-sm text-center"
                                    ),
                                ),
                                href=f"mailto:{State.current_investigator.email}",
                                # href=f"/investigador/{i}",
                            ),
                            align="center",
                            width="100%",
                            spacing="3",
                        ),
                        rx.box(
                            rx.text("Disciplinas OCDE nivel 2", color="white"),
                        ),
                        rx.cond(
                            State.current_investigator.ocde_2,
                            rx.flex(
                                rx.foreach(
                                    State.current_investigator.ocde_2.split(","),
                                    adaptive_badge,
                                ),
                                wrap="wrap",
                                spacing="3",
                                class_name="w-full p-2",
                            ),
                            rx.box(
                                rx.text(
                                    "No hay datos disponibles",
                                    class_name="text-white p-2",
                                ),
                            ),
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.image(
                                    src="/total_pro.png", class_name="w-1/2 h-1/2"
                                ),
                                rx.spacer(),
                                rx.text(
                                    "Proyectos: ", class_name="text-white text-base"
                                ),
                                rx.text(
                                    f"{State.filtered_count}",
                                    class_name="text-white text-lg font-semibold",
                                ),
                                class_name="items-center justify-center gap-2",
                            ),
                            rx.divider(size="4", class_name="w-1/2 bg-white"),
                            rx.hstack(
                                rx.image(
                                    src="/total_pub.png", class_name="w-1/2 h-1/2"
                                ),
                                rx.spacer(),
                                rx.text(
                                    "Publicaciones: ", class_name="text-white text-base"
                                ),
                                rx.text(
                                    f"{State.filtered_count_pub}",
                                    class_name="text-white text-lg font-semibold",
                                ),
                                class_name="items-center justify-center gap-2",
                            ),
                            spacing="2",
                            class_name="w-full rounded-lg mt-4 p-5 bg-gray-800/90",
                            # align="end",
                            # class_name="px-80"
                        ),
                        width="100%",
                        spacing="4",
                        class_name="w-full h-full text-left py-10",
                    ),
                    rx.flex(spacing="8"),
                    spacing="4",
                    class_name="w-full h-full text-left p-10",
                    background_image="url('/bg_perfil_mobile.png')",
                    border_radius="10px",
                    background_size="cover",
                    # background_size="auto auto",
                    background_repeat="no-repeat",
                    background_position="center",
                    overflow="hidden",
                ),
                height="100%",
                width="100%",
                # class_name="bg-indigo-300/85 shadow-lg p-10",
                # background_image="url('/bg_perfil.png')",
                gap="4",
                # class_name="py-20 text-left",
                # columns=Breakpoints(initial="1", sm="1", lg="4", xl="4"),
                # background="url('/bg_bio.png')",
            ),
            width="100%",
            class_name="p-5 text-left",
            spacing="2",
        ),
        rx.flex(
            rx.tabs.root(
                rx.tabs.list(
                    _tabs_trigger("Proyectos", "notebook-pen", value="projects"),
                    _tabs_trigger("Publicaciones", "scroll-text", value="publications"),
                    class_name="w-full flex flex-col sm:flex-row gap-2",
                ),
                rx.tabs.content(
                    main_table(),
                    value="projects",
                    class_name="w-full overflow-x-auto py-5 text-base",
                ),
                rx.tabs.content(
                    pub_table(),
                    value="publications",
                    class_name="w-full overflow-x-auto py-5 text-base",
                ),
                default_value="projects",
                width="100%",
                # class_name="py-5",
            ),
            class_name="w-full p-2 sm:p-10",
            spacing="0",
        ),
        rx.flex(
            rx.link(
                rx.button("Volver", cursor="pointer", class_name="bg-[#a280f6]"),
                href="/investigadoras",
                color="#a280f6",
                class_name="text-center px-10 py-5",
            ),
            width="100%",
            spacing="1",
        ),
        footer_inst(),
        width="100%",
        spacing="0",
        # background="url('/bg_inv.png')",
        background_color="#dfdfdf",
        # on_mount=State.load_grid_data,
    )


# Estilos personalizados
base_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
    "grid.css",
    "/loader.css",
]

# Estilos globales para todos los componentes
base_style = {
    rx.text: {
        "text_decoration": "none",
        "font_family": "Open Sans",
    },
    rx.heading: {
        "font_family": "Open Sans",
    },
    rx.link: {
        "text_decoration": "none",
    },
    rx.icon: {
        "text_decoration": "none",
    },
}

# Aplicación principal de Reflex, backend y frontend
app = rx.App(
    style=base_style,
    stylesheets=base_stylesheets,
    theme=rx.theme(
        has_background=True,
        radius="large",
        accent_color="indigo",
        appearance="light",
    ),
    head_components=[
        rx.script(
            src="https://badge.dimensions.ai/badge.js", async_=True, char_set="utf-8"
        ),
        rx.script(
            src="https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js",
        ),
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Inline:opsz,wght@10..72,100..900&family=Big+Shoulders:opsz,wght@10..72,100..900&family=Grenze+Gotisch:wght@100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Open+Sans:ital,wght@0,300..800;1,300..800&family=Outfit&family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Roboto+Mono:ital,wght@0,100..700;1,100..700&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap",
            rel="stylesheet",
        ),
    ],
)