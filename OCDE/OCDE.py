# from .backend.backend import (
#     State,
#     proyectos_2023, proyectos_2024,
#     inv_2023, inv_2024, ciencias_agricolas_2023, ciencias_naturales_2023, ciencias_sociales_2023,
#     ingenieria_tecnologia_2023, humanidades_2023, medicina_salud_2023, ciencias_agricolas_2024,
#     ciencias_naturales_2024, ciencias_sociales_2024, ingenieria_tecnologia_2024, humanidades_2024,
#     medicina_salud_2024, total_publicaciones_22, total_publicaciones_21
# )
from .backend.backend import State
from .views.navbar import navbar
from .views.table import main_table, pub_table
from .views.stats import stats_ui
from .views.contacto import contact_form
from .views.footer import footer
from .views.searchbar import navbar_searchbar, navbar_searchbar_notsearch
from .views.repositorio import repo_menu
from .views.home import huincha, contenido_home, superbanner, footer_inst, navbar_main, banner_generator

from .views.filtros import areas_selector
from .views.select_filtro import select_intro
from .views.card_inv import card_inv
import reflex as rx
from reflex.components.core.breakpoints import Breakpoints


def _tabs_trigger(text: str, icon: str, value: str):
    return rx.tabs.trigger(
        rx.hstack(
            rx.icon(icon, size=24),
            rx.heading(text, size="5"),
            spacing="2",
            align="center",
            width="100%",
        ),
        value=value,
    )

# @rx.page(route="/estadisticas", title="Inicio")
# def index() -> rx.Component:
#     return rx.vstack(
#         navbar(),
#         rx.flex(
#                 # spline2(scene=scene2),
#             rx.image(src="/data_center_vrip.jpg", width="100%", heigth="auto"),
#             height="400px",
#             width="100%",
#         ),
#         rx.box("Estadisticas de la plataforma", class_name="w-full text-center mb-4 text-2xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl p-10"),
#         rx.grid(
#             # Llamamos 3 veces a stats para generar 3 tarjetas
#             stats(stat_name="Investigadores en proyectos 2024", value=inv_2024, prev_value=inv_2023, icon="users", badge_color="blue"),
#             stats(stat_name="Proyectos 2024", value=proyectos_2024, prev_value=proyectos_2023, icon="notebook-pen", badge_color="indigo"),
#             stats(stat_name="Publicaciones 2022", value=total_publicaciones_22, prev_value=total_publicaciones_21, icon="scroll-text", badge_color="cyan"),
#             stats(stat_name="Ciencias Agrícolas 2024", value=ciencias_agricolas_2024, prev_value=ciencias_agricolas_2023, icon="sprout", badge_color="green"),
#             stats(stat_name="Ciencias Naturales 2024", value=ciencias_naturales_2024, prev_value=ciencias_naturales_2023, icon="flask-round", badge_color="teal"),
#             stats(stat_name="Ciencias Sociales 2024", value=ciencias_sociales_2024, prev_value=ciencias_sociales_2023, icon="user-round-search", badge_color="orange"),
#             stats(stat_name="Ingeniería y Tecnología 2024", value=ingenieria_tecnologia_2024, prev_value=ingenieria_tecnologia_2023, icon="cpu", badge_color="amber"),
#             stats(stat_name="Humanidades 2024", value=humanidades_2024, prev_value=humanidades_2023, icon="brain", badge_color="gold"),
#             stats(stat_name="Medicina y Ciencias de la Salud 2024", value=medicina_salud_2024, prev_value=medicina_salud_2023, icon="shield-plus", badge_color="tomato"),
    
#             columns=Breakpoints(base="1", md="2", lg="3"),     # 3 columnas
#             spacing="6",    # Espaciado entre las tarjetas
#             width="100%",   # Que ocupe todo el ancho posible
#             style={"margin": "0 auto", "padding": "40px", "maxWidth": "1200px"},
#             overflow="hidden",
#             position="relative",
#         ),
        
#         footer(),
#         width="100%",
#         spacing="0",
#         # background_image="url('/background.png')",
#         class_name="bg-gradient-to-r from-neutral-100 to-indigo-100"
      
#         # padding_x=["1.5em", "1.5em", "3em", "5em"],
#         # padding_y=["1.25em", "1.25em", "2em"],
#     )


# def stats(
#     stat_name: str = "Users",
#     value: int = 0,
#     prev_value: int = 0,
#     icon: str = "users",
#     badge_color: LiteralAccentColor = "blue",
#     total_items: int = None,
# ) -> rx.Component:
#     percentage_change = (
#         round(((value - prev_value) / prev_value) * 100, 2)
#         if prev_value != 0
#         else 0
#         if value == 0
#         else float("inf")
#     )
#     change = (
#         "aumento" if value > prev_value else "disminución"
#     )
#     arrow_icon = (
#         "trending-up"
#         if value > prev_value
#         else "trending-down"
#     )
#     arrow_color = (
#         "grass" if value > prev_value else "tomato"
#     )
#     return rx.card(
#         rx.vstack(
#             rx.hstack(
#                 rx.badge(
#                     rx.icon(tag=icon, size=34),
#                     color_scheme=badge_color,
#                     radius="full",
#                     padding="0.7rem",
#                 ),
#                 rx.vstack(
#                     rx.heading(
#                         f"{value:,}",
#                         size="6",
#                         weight="bold",
#                     ),
#                     rx.text(
#                         stat_name, size="4", weight="medium"
#                     ),
#                     spacing="1",
#                     height="100%",
#                     align_items="start",
#                     width="100%",
#                 ),
#                 height="100%",
#                 spacing="4",
#                 align="center",
#                 width="100%",
#             ),
#             rx.hstack(
#                 rx.hstack(
#                     rx.icon(
#                         tag=arrow_icon,
#                         size=24,
#                         color=rx.color(arrow_color, 9),
#                     ),
#                     rx.text(
#                         f"{percentage_change}%",
#                         size="3",
#                         color=rx.color(arrow_color, 9),
#                         weight="medium",
#                     ),
#                     spacing="2",
#                     align="center",
#                 ),
#                 rx.text(
#                     f"{change} desde el año pasado",
#                     size="2",
#                     color=rx.color("gray", 10),
#                 ),
#                 align="center",
#                 width="100%",
#             ),
#             spacing="3",
#         ),
#         size="3",
#         width="100%",
#         max_width="21rem",
#     )

# Página de inicio
@rx.page(route="/", title="Inicio")
def obs_inicio():
    return rx.vstack(
        huincha(),
        banner_generator("/banner_home.jpg"),
        navbar_main(),
        contenido_home(),
        superbanner(),
        footer_inst(),
        spacing="0",
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
            width="100%",           # Ancho 100% del contenedor
            class_name="sm:p-2 px-3 justify-center items-center", 
            style={"overflowX": "hidden"},
        ),
        superbanner(),
        footer_inst(),
        spacing="0",
    )

# Página de indicadores
@rx.page(route="/obs_otros_indicadores", title="Otros Indicadores")
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
            width="100%",           # Ancho 100% del contenedor
            class_name="sm:p-2 px-3 justify-center items-center", 
            style={"overflowX": "hidden"},
        ),
        superbanner(),
        footer_inst(),
        spacing="0",
    )


# Página de repositorio
@rx.page(route="/obs_repositorio", title="Repositorio")
def obs_repositorio():
    return rx.vstack(
        huincha(),
        banner_generator("/banner_repositorio.jpg"),
        navbar_main(),
        rx.flex(
            repo_menu(),
            class_name="w-1/2 p-5",
        ),
        superbanner(),
        footer_inst(),
        spacing="0",
        align="center",
        class_name="w-full"
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
            rx.html(
            """
            <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdbf9MB2Urtx5eaViOJrsusbcDuFEyBKOIy_d2cIIt5_vdx4Q/viewform?embedded=true" width="1000" height="1280" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
            """,
            class_name="p-10",
            ),
        ),
        rx.mobile_and_tablet(
            rx.html(
            """
            <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdbf9MB2Urtx5eaViOJrsusbcDuFEyBKOIy_d2cIIt5_vdx4Q/viewform?embedded=true" width="300" height="1280" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
            """,
            class_name="p-10",
            ),
        ),
        
        superbanner(),
        footer_inst(),
        spacing="0",
        align="center",
        background_image="url('/bg_inv.jpg')",
        background_size="cover",
        background_repeat="no-repeat",
        baclground_position="center",
    )

# Página de investigadores
@rx.page(route="/investigadoras", on_load=State.load_academicas)
def academicas():
    return rx.vstack(
        huincha(),
        banner_generator("/banner_home.jpg "),
        navbar_main(),
        navbar_searchbar(),
        areas_selector(),
        # select_intro(),
        rx.flex(
            rx.hstack(
                rx.foreach(
                    # Iteramos sobre la lista FILTRADA
                    State.filtered_investigators,
                    lambda inv, i: rx.card(
                        rx.vstack(
                            # ------------ Parte Superior de la Card -------------
                            rx.hstack(
                                rx.flex(
                                    # rx.icon(
                                    #     tag="scroll-text",
                                    #     size=34,
                                    #     class_name=(
                                    #         "transition-all duration-300"
                                    #         "rounded-lg cursor-pointer"
                                    #         "filter grayscale hover:grayscale-0"
                                    #     ),
                                    # ),
                                    rx.image(
                                        src="/icono_inv.png",
                                    ),
                                    # color_scheme="iris",
                                    radius="full",
                                    # padding="0.7rem",
                                ),
                                rx.vstack(
                                    rx.heading(
                                        inv["name"],  # Nombre del investigador
                                        class_name="text-base font-semibold text-indigo-900",
                                    ),
                                    rx.text(
                                        inv["grado_mayor"],  # Grado académico
                                        class_name="text-sm font-semibold flex items-center",
                                    ),
                                    spacing="4",
                                    width="100%",
                                ),
                                height="100%",
                                spacing="4",
                                align="center",
                                width="100%",
                            ),
                            # ------------ Parte Inferior de la Card -------------
                            rx.hstack(
                                rx.link(
                                    rx.image(src="/orcid_icon.png"),
                                    href=str(inv["orcid"]),
                                ),
                                rx.link(
                                    rx.button(
                                        rx.icon("circle-arrow-right", size=16),
                                        "Contactar",
                                        size="2",
                                        width="100%",
                                        cursor="pointer",
                                        class_name=(
                                            "text-white rounded-lg p-2.5"
                                            "font-medium text-sm text-center"
                                        ),
                                        background_color="#a280f6",
                                    ),
                                    href=f"/investigadora/{inv['id']}",
                                    # href=f"/investigador/{i}",
                                ),
                                justify="end",
                                width="100%",
                                spacing="3",
                            ),
                            spacing="3",
                        ),
                        size="3",
                        width="100%",
                        max_width="21rem",
                        box_shadow="lg",
                        # border_radius="0.5rem",
                        background_color="#DFDFDF",
                        # padding="1em",
                        class_name="p-5 md:m-5",
                    ),                   
                ),
                wrap="wrap",  # Para acomodar las tarjetas en varias filas
                justify="center",
            ),
            class_name="w-full md:px-40 p-5",  # padding alrededor
            flex="1",          # Para que crezca y el footer quede abajo
            spacing="3",
        ),
        footer_inst(),
        spacing="0",
        align="stretch",
        wrap="wrap",
        background_image="url('/bg_aca.jpg')",
        # background_size="cover",
        # background_repeat="no-repeat",
        # background_position="center",
        # background_color="#DFDFDF",
        width="100%",
        # min_height="100vh", # si quieres que ocupe el alto de la ventana
    )

# Página perfil del investigador
@rx.page(route="/investigadora/[id]", on_load=[State.load_entries_pub, State.load_entries, State.load_grid_data])
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
                            fallback=State.current_investigator.name[0],
                            variant="solid",
                            radius="full",
                            color_scheme="iris",
                            # background_color="#a280f6",
                            class_name="text-white",
                        ),
                        rx.box(
                            rx.text(f"{State.current_investigator.name}", class_name="text-3xl font-bold text-white p-2"),
                            rx.text(f"{State.current_investigator.grado_mayor}", class_name="text-white text-lg font-extralight p-2 break-words whitespace-normal"),
                            # rx.text(f"{State.current_investigator.ocde_2}", class_name="text-white text-base font-light p-2 break-words whitespace-normal"),
                            # rx.badge(f"{State.current_investigator.ocde_2}", class_name="text-indigo-600 font-light p-2 break-words whitespace-normal"),
                            # rx.cond(
                            #     State.current_investigator.magister is None,
                            #     rx.text(f"{State.current_investigator.magister}", class_name="text-indigo-600")
                            # ),
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
                                            rx.link("Click Aquí", href="https://orcid.org/"),
                                            class_name="text-sm text-gray-700 p-2"
                                        ),
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
                                rx.text("Disciplinas OCDE nivel 2", class_name="text-white p-2"),
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
                                rx.grid(
                                    rx.foreach(
                                        # Convertimos a lista y procesamos cada item
                                        State.current_investigator.ocde_2.split(","),
                                        lambda item: rx.tooltip(
                                            rx.badge(
                                                # Usamos operaciones Var compatibles
                                                rx.cond(
                                                    item.strip().length() > 20,
                                                    item.strip()[:18] + "...",
                                                    item.strip()
                                                ),
                                                size="3",
                                                variant="solid",
                                                color_scheme="iris",
                                                high_contrast=False,
                                                class_name="text-xs font-mono text-center"
                                            ),
                                            content=item,
                                            class_name="bg-[#a280f6] font-mono text-center"
                                        )
                                    ),
                                    columns=Breakpoints(initial="1", sm="2", md="3", lg="3", xl="3"),
                                    spacing="2",
                                    class_name="w-full py-5"
                                ),
                                rx.box(
                                    rx.text("No hay datos disponibles", class_name="text-white p-2"),
                                )  
                            ),
                            spacing="4",
                            class_name="p-2",
                            width="100%",
                        ),
                        rx.spacer(),
                        rx.vstack(
                            # card_inv(name=rx.html("TOTAL<br> PROYECTOS"), description=State.filtered_count),
                            # card_inv(name=rx.html("TOTAL<br> PUBLICACIONES"), description=State.filtered_count_pub),
                            rx.hstack(
                                rx.image(src="/total_pro.png"),
                                rx.spacer(),
                                rx.text("Proyectos: ", class_name="text-white text-xl"),
                                rx.text(f"{State.filtered_count}", class_name="text-white text-2xl font-semibold"),
                                class_name="items-center justify-center gap-2"
                            ),
                            rx.divider(size="4", class_name="w-3/4 bg-white"),
                            rx.hstack(
                                rx.image(src="/total_pub.png"),
                                rx.spacer(),
                                rx.text("Publicaciones: ", class_name="text-white text-xl"),
                                rx.text(f"{State.filtered_count_pub}", class_name="text-white text-2xl font-semibold"),
                                class_name="items-center justify-center gap-2"
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
                            fallback=State.current_investigator.name[0],
                            radius="full",
                            variant="solid",
                            color_scheme="iris",
                            # background_color="#a280f6",
                            class_name="text-white",
                        ),
                        rx.box(
                            rx.text(f"{State.current_investigator.name}", class_name="text-2xl font-semibold text-white p-1"),
                            rx.text(f"{State.current_investigator.grado_mayor}", class_name="text-white p-1"),
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
                                rx.grid(
                                    rx.foreach(
                                        # Convertimos a lista y procesamos cada item
                                        State.current_investigator.ocde_2.split(","),
                                        lambda item: rx.tooltip(
                                            rx.badge(
                                                # Usamos operaciones Var compatibles
                                                rx.cond(
                                                    item.strip().length() > 14,
                                                    item.strip()[:14] + "...",
                                                    item.strip()
                                                ),
                                                size="3",
                                                variant="solid",
                                                color_scheme="iris",
                                                high_contrast=False,
                                                class_name="text-xs font-mono"
                                            ),
                                            content=item,
                                            class_name="bg-[#a280f6] font-mono"
                                        )
                                    ),
                                    columns=Breakpoints(initial="2", sm="2"),
                                    spacing="2",
                                    class_name="w-full py-5"
                                ),
                                rx.box(
                                    rx.text("No hay datos disponibles", class_name="text-white p-2"),
                                ) 
                            ),
                        rx.vstack(
                            rx.hstack(
                                rx.image(src="/total_pro.png", class_name="w-1/2 h-1/2"),
                                rx.spacer(),
                                rx.text("Proyectos: ", class_name="text-white text-base"),
                                rx.text(f"{State.filtered_count}", class_name="text-white text-lg font-semibold"),
                                class_name="items-center justify-center gap-2"
                            ),
                            rx.divider(size="4", class_name="w-1/2 bg-white"),
                            rx.hstack(
                                rx.image(src="/total_pub.png", class_name="w-1/2 h-1/2"),
                                rx.spacer(),
                                rx.text("Publicaciones: ", class_name="text-white text-base"),
                                rx.text(f"{State.filtered_count_pub}", class_name="text-white text-lg font-semibold"),
                                class_name="items-center justify-center gap-2"
                            ),
                            spacing="2",
                            class_name="w-full rounded-lg mt-4 p-5 bg-transparent/75",
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
                    class_name="flex flex-col sm:flex-row gap-2",
                    width="100%",
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
            rx.link(rx.button("Volver", cursor="pointer", class_name="bg-[#a280f6]"), href="/investigadoras", color="#a280f6", class_name="text-center px-10 py-5"),
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
]

# Estilos globales para todos los componentes
base_style = {
    "font_family": "Roboto",
    rx.text: {
        "text_decoration": "none",
        "font_family": "Roboto",
    },
    rx.heading: {
        "font_family": "sans-serif",
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
        has_background=True, radius="large", accent_color="indigo",
        appearance="light", 
    ),
    head_components=[
        rx.script(
            src="https://badge.dimensions.ai/badge.js",
            async_=True,
            char_set="utf-8"
        ),
        rx.script(
            src="https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js",
        ),
    ]
    
)
