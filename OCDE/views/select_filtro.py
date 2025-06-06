import reflex as rx

AREAS = ["Química", "Biología", "Física", "Matemática"]

class SelectState(rx.State):
    value: str = "Selecciona una opción"

    @rx.event
    def change_value(self, value: str):
        """Change the select value var."""
        self.value = value

def select_intro():
    return rx.center(
        rx.select(
            AREAS,
            value=SelectState.value,
            on_change=SelectState.change_value,
        ),
        rx.badge(SelectState.value),
    )
