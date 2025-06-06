import reflex as rx
from ..backend.backend import State
import smtplib
from email.mime.text import MIMEText
def form_field(
    label: str, placeholder: str, type: str, name: str
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            rx.form.control(
                rx.input(
                    placeholder=placeholder, type=type
                ),
                as_child=True,
            ),
            direction="column",
            spacing="1",
        ),
        name=name,
        width="100%",
    )


def contact_form() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="mail-plus", size=32),
                    color_scheme="blue",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.heading(
                        "Si tienes alguna consulta o sugerencia, no dudes en escribirnos.",
                        size="4",
                        weight="bold",
                    ),
                    rx.text(
                        "Completa el formulario que aparece a continuación y nuestro equipo se pondrá en contacto contigo lo antes posible. ",
                        size="2",
                    ),
                    spacing="1",
                    height="100%",
                ),
                height="100%",
                spacing="4",
                align_items="center",
                width="100%",
            ),
            rx.form.root(
                rx.flex(
                    rx.flex(
                        form_field(
                            "Nombre",
                            "Ingresa tu nombre",
                            "text",
                            "name",
                        ),
                        form_field(
                            "Institución o Afiliación",
                            "Ingresa tu institución",
                            "text",
                            "institucion",
                        ),
                        spacing="3",
                        flex_direction=[
                            "column",
                            "row",
                            "row",
                        ],
                    ),
                    rx.flex(
                        form_field(
                            "Email",
                            "user@reflex.dev",
                            "email",
                            "email",
                        ),
                        form_field(
                            "Ciudad/País", "Ingresa tu ciudad/país", "text", "city"
                        ),
                        spacing="3",
                        flex_direction=[
                            "column",
                            "row",
                            "row",
                        ],
                    ),
                    rx.flex(
                        rx.text(
                            "Mensaje",
                            style={
                                "font-size": "15px",
                                "font-weight": "500",
                                "line-height": "35px",
                            },
                        ),
                        rx.text_area(
                            placeholder="Escribe tu mensaje...",
                            name="message",
                            resize="vertical",
                        ),
                        direction="column",
                        spacing="1",
                    ),
                    rx.form.submit(
                        rx.button("Enviar", size="1", color_scheme="blue", radius="full", class_name="w-32 items-center justify-center"),
                        as_child=True,
                        class_name="items-center justify-center",
                    ),
                    direction="column",
                    spacing="2",
                    width="100%",
                ),
                on_submit=State.handle_submit,
                reset_on_submit=False,
            ),
            width="100%",
            direction="column",
            spacing="4",
        ),
        size="3",
        class_name="w-full justify-center items-center",
    )