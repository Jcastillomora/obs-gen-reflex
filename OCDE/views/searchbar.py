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
                    align_items="center",
                ),
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
        top="0px",
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
        top="0px",
        width="100%",
        spacing="0",
        background_color="#a280f6",
        class_name="p-5",
    )
