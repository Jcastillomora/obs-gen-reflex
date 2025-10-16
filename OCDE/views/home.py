import reflex as rx


def home_card(
    icon: str = "",
    title: str = "Analizamos y Visualizamos",
    description: str = "datos sobre participación y trayectorias de Investigadoras",
    color: str = "indigo",
) -> rx.Component:
    """A visually stunning card component with animations and customizable content."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                # Background effects layer
                rx.el.div(
                    rx.el.div(
                        class_name=f"absolute inset-0 bg-gradient-to-tr from-{color}-500/5 to-{color}-400/10 opacity-40 group-hover:opacity-60 transition-opacity duration-500"
                    ),
                    rx.el.div(
                        class_name=f"absolute -bottom-20 -left-20 w-48 h-48 rounded-full bg-gradient-to-tr from-{color}-500/10 to-transparent blur-3xl opacity-30 group-hover:opacity-50 transform group-hover:scale-110 transition-all duration-700 animate-bounce delay-500"
                    ),
                    rx.el.div(
                        class_name=f"absolute top-10 left-10 w-16 h-16 rounded-full bg-{color}-500/5 blur-xl animate-ping"
                    ),
                    rx.el.div(
                        class_name=f"absolute bottom-16 right-16 w-12 h-12 rounded-full bg-{color}-500/5 blur-lg animate-ping delay-1000"
                    ),
                    rx.el.div(
                        class_name=f"absolute inset-0 bg-gradient-to-r from-transparent via-{color}-500/5 to-transparent transform -skew-x-12 translate-x-full group-hover:translate-x-[-200%] transition-transform duration-1000"
                    ),
                    class_name="absolute inset-0 z-0 overflow-hidden",
                ),
                
                # Content layer
                rx.el.div(
                    rx.el.div(
                        # Icon/Image container with animations
                        rx.el.div(
                            rx.el.div(
                                class_name=f"absolute inset-0 rounded-full border-2 border-{color}-500/20 animate-ping"
                            ),
                            rx.el.div(
                                class_name=f"absolute inset-0 rounded-full border border-{color}-500/10 animate-pulse delay-500"
                            ),
                            rx.el.div(
                                rx.el.div(
                                    # Aquí va la imagen personalizable
                                    rx.icon(
                                        icon,
                                        alt="Card icon",
                                        class_name="w-16 h-16 object-contain",
                                    ),
                                    class_name="transform group-hover:rotate-180 transition-transform duration-700",
                                ),
                                class_name=f"p-6 rounded-full backdrop-blur-lg border border-{color}-500/20 bg-gradient-to-br from-black/80 to-gray-900/60 shadow-2xl transform group-hover:rotate-12 group-hover:scale-110 transition-all duration-500 hover:shadow-{color}-500/20",
                            ),
                            class_name="relative mb-6",
                        ),
                        
                        # Title
                        rx.el.div(
                            rx.text(
                                title,
                                class_name=f"text-3xl font-bold bg-gradient-to-r from-{color}-400 via-{color}-500 to-{color}-400 bg-clip-text text-transparent",
                            ),
                            class_name="mb-4 transform group-hover:scale-105 transition-transform duration-300",
                        ),
                        
                        # Description
                        rx.el.div(
                            rx.text(
                                description,
                                class_name="text-gray-300 text-sm text-center leading-relaxed transform group-hover:text-gray-200 transition-colors duration-300",        
                            ),
                            class_name="space-y-1 max-w-sm",
                        ),
                        
                        # Decorative line
                        rx.el.div(
                            class_name=f"mt-6 w-1/3 h-0.5 bg-gradient-to-r from-transparent via-{color}-500 to-transparent rounded-full transform group-hover:w-1/2 group-hover:h-1 transition-all duration-500 animate-pulse"
                        ),
                        
                        class_name="flex flex-col items-center text-center",
                    ),
                    class_name="p-8 relative z-10",
                ),
                
                # Corner decorations
                rx.el.div(
                    class_name=f"absolute top-0 left-0 w-20 h-20 bg-gradient-to-br from-{color}-500/10 to-transparent rounded-br-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                ),
                rx.el.div(
                    class_name=f"absolute bottom-0 right-0 w-20 h-20 bg-gradient-to-tl from-{color}-500/10 to-transparent rounded-tl-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                ),
            ),
            class_name=f"text-white rounded-3xl border border-{color}-500/20 bg-gradient-to-tr from-[#0F0F0F] to-[#0B0B0B] shadow-2xl duration-700 z-10 relative backdrop-blur-xl hover:border-{color}-500/40 overflow-hidden hover:shadow-{color}-500/10 hover:shadow-3xl w-[350px]",
        ),
        class_name="group cursor-pointer transform transition-all duration-500 hover:scale-105 hover:-rotate-1",
    )


def loader_box(box_number: int) -> rx.Component:
    """A single box in the loader."""
    return rx.el.div(
        rx.el.div(class_name="side-left"),
        rx.el.div(class_name="side-right"),
        rx.el.div(class_name="side-top"),
        class_name=f"box box-{box_number}",
    )

def loader() -> rx.Component:
    """The loader component."""
    return rx.el.div(
        rx.el.div(
            loader_box(1),
            loader_box(2),
            loader_box(3),
            loader_box(4),
            class_name="loader",
        ),
        class_name="flex items-center justify-center p-10",
    )

#Huincha principal
def huincha():
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.image(
                    src="/barra_colores.png",
                    class_name="flex max-w-full h-auto", 
                ),
                rx.flex(
                    rx.link(
                        rx.desktop_only(
                            rx.image(
                                src="https://repositorio.ufro.cl/files/asset/4bb0d7977fd459601547426a87de36f061a4797f.png",
                                width="200px",
                                class_name="px-5 h-full"
                            ),
                        ),
                        rx.mobile_only(
                            rx.image(
                                src="https://repositorio.ufro.cl/files/asset/4bb0d7977fd459601547426a87de36f061a4797f.png",
                                width="150px",
                                class_name="px-5 h-full"
                            ),
                        ),
                        href="https://www.ufro.cl/",
                        is_external=True,
                        class_name="no-underline flex items-center"
                    ),
                    # rx.divider(orientation="vertical", size="2", color_scheme="gray"),
                    rx.link(
                        rx.desktop_only(
                            rx.image(
                                src="https://repositorio.ufro.cl/files/asset/7aa7a9987e0c4756b844636f0aa84d9a2023c5ef.png",
                                width="200px",
                                class_name="px-5 h-full"
                            ),
                        ),
                        rx.mobile_only(
                            rx.image(
                                src="https://repositorio.ufro.cl/files/asset/7aa7a9987e0c4756b844636f0aa84d9a2023c5ef.png",
                                width="150px",
                                class_name="px-5 h-full"
                            ),
                        ),

                        href="https://vrip.ufro.cl/",
                        is_external=True,
                        class_name="no-underline flex items-center"
                    ),
                    align_items="center",
                    class_name="flex items-center text-white text-2xl font-light"
                ),
                # rx.flex(
                #     rx.color_mode.button(),
                #     justify="end",
                #     class_name="px-10"
                # ),
                class_name="flex flex-wrap items-center w-full",
                # justify="between",
            ),
        ),
        class_name="w-full",
        style={"backgroundColor": "#005fab"}
    )

def banner_generator(image: str) -> rx.Component:
    return rx.box(
        rx.image(
            src=image,
            class_name="w-full h-auto",
            alt="Responsive image"
        ),
        class_name="relative"
    )


def navbar_link(text: str, url: str) -> rx.Component:
    return rx.link(
        rx.text(text, size="4", class_name="text-black font-semibold hover:text-indigo-500"), href=url
    )

def navbar_link_dropdown(text: str, url: str) -> rx.Component:
    return rx.link(
        rx.text(text, size="3", class_name="bg-slate-300 p-2 text-black font-semibold hover:text-indigo-500"), href=url
    )

#Navbar principal
def navbar_main() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    navbar_link("Inicio", "/"),
                    # navbar_link("Indicadores", "/obs_indicadores"),
                    rx.menu.root(
                        rx.menu.trigger(
                            rx.button(
                                rx.text(
                                    "Indicadores",
                                    size="4",
                                    weight="medium",
                                    class_name="text-black font-semibold hover:text-indigo-500",
                                ),
                                rx.icon("chevron-down"),
                                weight="medium",
                                variant="ghost",
                                size="3",
                                class_name="text-black font-semibold hover:text-indigo-500",
                            ),
                        ),
                        rx.menu.content(
                            navbar_link_dropdown("Indicadores ANID", "/obs_indicadores"),
                            navbar_link_dropdown("Otros Indicadores", "/obs_otros_indicadores"),
                            class_name="bg-slate-300 rounded-md shadow-md",
                        ),
                    ),
                    navbar_link("Repositorio", "/obs_repositorio"),
                    navbar_link("Investigadoras", "/investigadoras"),
                    navbar_link("Contacto", "/obs_contacto"),
                    justify="center",
                    spacing="9",
                ),
                align_items="center",
                class_name="p-5 justify-center text-black"
            ),
        ),
        rx.mobile_and_tablet(
            rx.hstack(
                rx.menu.root(
                    rx.text("Menú", class_name="text-black font-semibold hover:text-indigo-500"),
                    rx.menu.trigger(
                        rx.icon("menu", size=30, class_name="text-black font-semibold hover:text-indigo-500")
                    ),
                    rx.menu.content(
                        rx.menu.item(navbar_link("Inicio", "/")),
                        # rx.menu.item(navbar_link("Indicadores", "/obs_indicadores")),
                        rx.menu.root(
                            rx.menu.trigger(
                                rx.button(
                                    rx.text(
                                        "Indicadores",
                                        size="4",
                                        weight="medium",
                                        class_name="text-black font-semibold hover:text-indigo-500",
                                    ),
                                    rx.icon("chevron-down"),
                                    weight="medium",
                                    variant="ghost",
                                    size="3",
                                    class_name="text-black font-semibold hover:text-indigo-500",
                                ),
                            ),
                            rx.menu.content(
                                navbar_link_dropdown("Indicadores ANID", "/obs_indicadores"),
                                navbar_link_dropdown("Otros Indicadores", "/obs_otros_indicadores"),
                                class_name="bg-slate-300 rounded-md shadow-md",
                            ),
                        ),
                        rx.menu.item(navbar_link("Repositorio", "/obs_repositorio")),
                        rx.menu.item(navbar_link("Investigadoras", "/investigadoras")),
                        rx.menu.item(navbar_link("Contacto", "/obs_contacto")),
                        spacing="5",
                        color_scheme="indigo",
                         class_name="bg-slate-400 rounded-md shadow-md"
                    ),
                    justify="end",
                ),
                justify="center",
                align_items="center",
                variant="soft",
            ),
        ),
        padding="1em",
        # position="fixed",
        # top="0px",
        # z_index="5",
        class_name="w-full bg-slate-300 shadow-md",
    )

#Contenido de la página de inicio
def contenido_home():
    return rx.box(
        rx.vstack(
            rx.box(
                rx.text("El Observatorio de Género y Ciencia de la Universidad de La Frontera tiene como objetivo principal aportar al desarrollo de capacidades institucionales a través del monitoreo de las acciones de transversalización del enfoque de género desde una perspectiva procedimental y normativa en el ámbito de I+D+i+e de base científica tecnológica en la institución.", class_name="text-indigo-900 text-left antialiased text-base sm:text-xs md:text-lg lg:text-xl leading-relaxed"),
                class_name="w-full bg-slate-300 rounded-lg shadow-lg p-6",
            ),
            class_name="w-full text-center p-4 sm:p-4 md:p-30 lg:p-30 xl:p-30",
        ),
        rx.flex(
            home_card("chart-pie", title="Monitoreamos", description="la participación de las investigadoras en proyectos y publicaciones", color="orange"),
            home_card("scan-eye", title="Visualizamos", description="la distribución de las investigadoras según áreas de conocimiento y líneas de investigación", color="violet"),
            home_card("file-chart-column", title="Reportamos", description="hallazgos clave sobre la participación de las investigadoras", color="gray"),
            class_name="justify-center gap-x-30 gap-y-10 flex-wrap py-5",
        ),
        # background_image="url('/bg_inv.png')",
        # background_size="cover",
        class_name="w-full bg-slate-200 sm:p-6 md:px-10 lg:px-20 xl:px-40",
    )

#Superbanner de la página de inicio
def superbanner():
    return rx.flex(
        rx.box(
            rx.vstack(
            rx.text("Contáctanos", class_name="text-orange-400"),
            rx.link(rx.text(rx.icon("chevrons-right"), class_name="text-orange-400 font-bold"), href="/obs_contacto"),
            background_color="#00FF0000",
            spacing="0",
            class_name="flex items-center justify-center border-2 border-orange-400 px-20 py-10"
            ),
        ),
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text("Síguenos en", class_name="text-white font-bold"),
                    rx.text("nuestras redes", class_name="text-white font-bold"),
                    spacing="0",
                ),
                rx.badge(
                    rx.link(
                        rx.icon("linkedin", size=30, class_name="text-4xl"),
                        href="https://www.linkedin.com/in/generoencienciaufro/",
                        class_name="text-white"
                    ),
                    radius="full",
                    variant="soft",
                    color_scheme="gray",
                    ),
                rx.badge(
                    rx.link(
                        rx.icon("instagram", size=30, class_name="text-4xl"),
                        href="https://www.instagram.com/generoenciencia.ufro/",
                        class_name="text-white"
                    ),
                    radius="full",
                    variant="soft",
                    color_scheme="gray",
                    ),
                class_name="text-center items-center justify-center px-20 py-10",
                spacing="5",
            ),
        ),
        background_image="url('/superbanner_home.jpg')",
        background_size="cover",
        background_position="center",
        background_repeat="no-repeat",
        class_name="h-full w-full text-2xl text-white p-32 flex-col md:flex-row",
        spacing="9",
        justify_content="center",
    )


def footer_item(text: str, href: str) -> rx.Component:
    return rx.link(
        rx.text(text),
        href=href,
        class_name="uk-link-reset text-white"  # Ajusta clases a tu gusto
    )

def social_link(src: str, href: str) -> rx.Component:
    return rx.link(
        rx.image(src=src, class_name="h-6 w-6"), 
        href=href
    )

def footer_brand() -> rx.Component:
    return rx.vstack(
        # Logo
        rx.image(
            src="https://vrip.ufro.cl/wp-content/uploads/2022/03/newRecurso-1diufro_.svg",
            class_name="w-72 h-20"
        ),
        # Texto principal
        rx.html(
            "<p>Universidad de La Frontera<br>Avenida Francisco Salazar 01145<br>Temuco, Chile<br>Casilla 54-D</p>",
            class_name="text-white text-xl"
        ),
        # Box con ícono teléfono y texto
        rx.box(
            rx.text(
                "Fono: (56) 45 232 5000  FAX:(56) 45 259 2822", 
                class_name="text-xl text-white"
            ),
            class_name="space-x-2"
        ),
        # Redes Sociales (Flickr, LinkedIn, YouTube, X, Instagram, Facebook)
        rx.hstack(
            social_link("/flickr.png",  "https://www.flickr.com/photos/vripufro/"),
            social_link("/linkedin.png","https://www.linkedin.com/company/vrip-ufro/?viewAsMember=true"),
            social_link("/youtube.png", "https://www.youtube.com/channel/UC1r3rR0lF0198Sil7QCyk1g"),
            social_link("/x.png",       "https://x.com/i/flow/login?redirect_after_login=%2Fvripufro"),
            social_link("/instagram.png","https://www.instagram.com/vripufro/?hl=en"),
            social_link("/facebook.png","https://www.facebook.com/vripufro/"),
            spacing="3"
        ),
        align_items="start",
        spacing="4",
    )

def footer_la_universidad() -> rx.Component:
    return rx.vstack(
        rx.heading("La Universidad", size="4", weight="bold", class_name="text-white text-lg md:text-xl lg:text-2xl py-6"),
        footer_item("> Historia Institucional",       "https://www.ufro.cl/index.php/inicio/institucional/historia"),
        footer_item("> Acreditación Institucional",   "https://www.ufro.cl/index.php/inicio/institucional/acreditacion"),
        footer_item("> Campus",                  "https://www.ufro.cl/index.php/inicio/institucional/campus"),
        footer_item("> Postulantes",                  "https://www.ufro.cl/index.php/postulantes"),
        footer_item("> Estudiantes",                  "https://www.ufro.cl/index.php/estudiantes"),
        footer_item("> Alumni",                    "https://alumni.ufro.cl"),
        footer_item("> Funcionarios",                 "https://www.ufro.cl/index.php/funcionarios"),
        align_items="start",
        spacing="0",
    )

def footer_accesos_rapidos() -> rx.Component:
    return rx.vstack(
        rx.heading("Accesos Rápidos", size="4", weight="bold", class_name="text-white text-lg md:text-xl lg:text-2xl py-6"),
        footer_item("> Trabaja con Nosotros",         "https://extranet.ufro.cl/concursos/"),
        footer_item("> Nuestras Licitaciones",        "https://www.mercadopublico.cl/Portal/Modules/Site/Busquedas/BuscadorAvanzado.aspx?qs=1"),
        footer_item("> Transparencia Activa",         "https://transparencia.ufro.cl/"),
        footer_item("> Solicitud de información\nley de Transparencia",  "https://www2.ufro.cl/transparencia/"),
        footer_item("> Ley de Lobby",                 "https://leylobby.ufro.cl/"),
        footer_item("> Portal de Pagos",              "https://pagoweb.ufro.cl/"),
        footer_item("> Verificador de Certificados",  "https://certificados.ufro.cl/ValidaCertificado.php"),
        align_items="start",
        spacing="0",
    )

#Footer principal
def footer_inst() -> rx.Component:
    return rx.el.footer(
        rx.vstack(
            # Primera "fila": tres columnas
            rx.flex(
                footer_brand(),         # Columna 1
                rx.divider(orientation="vertical", size="4", color="white"),
                footer_la_universidad(),# Columna 2
                rx.divider(orientation="vertical", size="4"),
                footer_accesos_rapidos(),# Columna 3
                justify="between",
                spacing="6",
                flex_direction=["column", "column", "row"],  
                # ↑ Esto hace que en pantallas pequeñas se apilen (column),
                #   y en grandes se muestren en fila (row).
                width="100%",
            ),
            # Si quieres un separador visual
            # rx.divider(),
            # Segunda "fila": Ej. algún disclaimer o Copyright
            # rx.text("© 2025 Universidad de La Frontera. Todos los derechos reservados.", class_name="text-white text-sm"),
            spacing="6",
            width="100%",
        ),
        # Estilos globales del footer
        width="100%",
        class_name="md:px-40 md:py-10 p-5 bg-[#005fab] font-sans text-white"
    )
