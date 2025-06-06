import reflex as rx

def card_inv(name: str, description: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="scroll-text", size=28, class_name="transition-all duration-300 rounded-lg cursor-pointer filter grayscale hover:grayscale-0"),  # Icono de usuario
                    color_scheme="blue",  # Color de la insignia
                    radius="full",
                    padding="0.7rem",
                ),
                rx.vstack(
                    rx.heading(
                        name,  # Nombre del usuario
                        size="1",
                        weight="bold",
                        class_name="text-center",
                    ),
                    rx.text(
                        description, # Descripción del usuario
                        size="5", 
                        weight="bold",
                        class_name="text-center",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="center",
                    width="100%",
                ),
                height="100%",
                spacing="2",
                align="center",
                width="100%",
            ),
            align="center",
            width="100%",
        ),
        align="center",
        size="3",
        width="auto",
        max_width="21rem",
        class_name="bg-transparent hover:bg-indigo-700",
    )