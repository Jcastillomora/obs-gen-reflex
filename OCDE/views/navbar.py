import reflex as rx

def navbar():
    return rx.flex(
        rx.hstack(
            rx.image(src="/logo_ufro.png", height="46px"),
            rx.heading("Proyectos de Investigación UFRO", size="7", class_name="text-transparent bg-clip-text bg-gradient-to-r from-gray-700 to-black"),
            rx.badge(
                "2018-2024",
                rx.icon("calendar", size=14),
                radius="full",
                align="center",
                color_scheme="blue",
                variant="surface",
            ),
            align="center",
        ),
        rx.spacer(),
        rx.hstack(
            rx.logo(),
            rx.color_mode.button(),
            align="center",
            spacing="3",
        ),
        # spacing="2",
        flex_direction=["column", "column", "row"],
        align="center",
        width="100%",
        top="0px",
        padding_x=["1.5em", "1.5em", "3em", "5em"],
        padding_y=["1.25em", "1.25em", "2em"],
        class_name="bg-gradient-to-r from-sky-400 to-blue-500",
    )
