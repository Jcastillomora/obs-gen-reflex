import reflex as rx


def repositorio_loader() -> rx.Component:
    """Loader animado para la sección de repositorio."""
    return rx.box(
        rx.box(
            rx.box(
                "loading ",
                rx.box(
                    rx.el.span("reportes", class_name="loader-repo-word"),
                    rx.el.span("documentos", class_name="loader-repo-word"),
                    class_name="loader-repo-words",
                ),
                class_name="loader-repo",
            ),
            class_name="loader-repo-card",
        ),
        class_name="loader-repo-container",
    )
