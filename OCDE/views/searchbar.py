import reflex as rx
from ..backend.backend import State

def navbar_searchbar() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    rx.icon(
                        "user-round-search",
                        width="2.25em",
                        height="auto",
                        border_radius="25%",
                        size=24,
                        class_name="text-indigo-900"
                    ),
                    rx.vstack(
                        rx.heading(
                            "Investigadoras", size="7", weight="bold", class_name="text-indigo-900"
                        ),
                        rx.text("Proyectos y Publicaciones 2018 - 2024", size="5", class_name="text-indigo-900"),
                        spacing="0",
                    ),
                    # rx.badge(
                    #     "2018-2024",
                    #     rx.icon("calendar", size=24),
                    #     radius="full",
                    #     align="center",
                    #     color_scheme="blue",
                    #     variant="surface",
                    # ),
                    align_items="center",
                ),
                # rx.input(
                #     rx.input.slot(rx.icon("search")),
                #     rx.input.slot(
                #         rx.icon("x", on_click=lambda: State.set_search_term("")),
                #         justify="end",
                #         cursor="pointer",
                #     ),
                #     value=State.search_term,
                #     placeholder="Buscar Investigadoras",
                #     size="2",
                #     max_width="250px",
                #     width="100%",
                #     variant="classic",
                #     color_scheme="indigo",
                #     on_change=lambda val: State.set_search_term(val),
                # ),
                justify="between",
                align_items="center",
                spacing="0",
                width="100%",
                top="0px",
                class_name="px-40",
            ),
        ),
        rx.mobile_and_tablet(
            rx.hstack(
                rx.hstack(
                    # rx.icon(
                    #     "user-round-search",
                    #     size=20,
                    #     width="2em",
                    #     height="auto",
                    #     border_radius="25%",
                    # ),
                    rx.vstack(
                        rx.heading(
                            "Investigadoras", size="4", weight="bold", class_name="text-indigo-900"
                        ),
                        rx.text("Proyectos y Publicaciones 2018-2024", size="1", class_name="text-indigo-900"),
                        spacing="0",
                    ),
                    align_items="center",
                ),
                # rx.input(
                #     rx.input.slot(rx.icon("search", size=15)),
                #     rx.input.slot(
                #         rx.icon("x", size=15),
                #         justify="end",
                #         cursor="pointer",
                #     ),
                #     value=State.search_term,
                #     placeholder="Buscar...",
                #     size="1",
                #     type="search",
                #     justify="end",
                #     width="50%",
                #     variant="surface",
                #     color_scheme="gray",
                #     on_change=lambda val: State.set_search_term(val),
                # ),
                justify="between",
                align_items="center",
                class_name="w-full",
            ),
        ),
        # bg=rx.color("accent", 3),
        # padding="1em",
        # position="fixed",
        top="0px",
        # z_index="5",
        width="100%",
        spacing="0",
        background_color="#a280f6",
        class_name="md:px-20 p-5",
    )


def navbar_searchbar_notsearch() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    rx.icon(
                        "user-round-search",
                        width="2.25em",
                        height="auto",
                        border_radius="25%",
                        size=24,
                        class_name="text-indigo-900"
                    ),
                    rx.vstack(
                        rx.heading(
                            "Investigadoras", size="7", weight="bold", class_name="text-indigo-900"
                        ),
                        rx.text("Proyectos y Publicaciones 2018 - 2024", size="5", class_name="text-indigo-900"),
                        spacing="0",
                    ),
                    # rx.badge(
                    #     "2018-2024",
                    #     rx.icon("calendar", size=24),
                    #     radius="full",
                    #     align="center",
                    #     color_scheme="blue",
                    #     variant="surface",
                    # ),
                    align_items="center",
                ),
                justify="between",
                align_items="center",
                spacing="0",
                top="0px",
                class_name="w-full px-10",
            ),
        ),
        rx.mobile_and_tablet(
            rx.hstack(
                rx.hstack(
                    rx.icon(
                        "user-round-search",
                        size=20,
                        width="2em",
                        height="auto",
                        border_radius="25%",
                        class_name="text-indigo-900"
                    ),
                    rx.vstack(
                        rx.heading(
                            "Investigadoras", size="4", weight="bold", class_name="text-indigo-900"
                        ),
                        rx.text("Proyectos y Publicaciones 2018-2024", size="1", class_name="text-indigo-900"),
                        spacing="0",
                    ),
                    align_items="center",
                ),
                justify="between",
                align_items="center",
                class_name="w-full",
            ),
        ),
        # bg=rx.color("accent", 3),
        # padding="1em",
        # position="fixed",
        top="0px",
        # z_index="5",
        width="100%",
        spacing="0",
        background_color="#a280f6",
        class_name="p-5",
    )
