import reflex as rx
from ..backend.backend import State


def optimized_ai_search_input() -> rx.Component:
    """
    Input de búsqueda AI.
    Búsqueda SOLO cuando presiona Enter o botón.
    """
    return rx.input(
        placeholder="Describe lo que buscas: 'investigadoras en energías renovables' o 'expertas en biotecnología'...",
        value=State.ai_search_input,
        on_change=State.set_ai_search_input.debounce(300),
        on_key_down=State.handle_ai_search_enter.debounce(300),
        size="3",
        style={
            "flex": "1",
            "border": "2px solid rgb(229, 231, 235)",
            "borderRadius": "8px",
            "padding": "12px 16px",
            "fontSize": "16px",
            "outline": "none",
            "transition": "border-color 0.05s ease",
            "willChange": "border-color",
            "contain": "layout style paint",
        },
        class_name="focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200",
        spell_check=False,
    )


def ai_search_box() -> rx.Component:
    """
    Componente de búsqueda potenciada por IA para investigadoras.
    """
    return rx.vstack(
        rx.hstack(
            rx.heading(
                "Buscar Investigadoras con IA",
                class_name="text-lg sm:text-xl text-gray-700 font-semibold",
            ),
            rx.badge(
                rx.icon("sparkles", size=14),
                "Beta",
                color_scheme="purple",
                variant="soft",
                size="1",
            ),
            spacing="3",
            align="center",
        ),
        rx.text(
            "Usa lenguaje natural para encontrar investigadoras específicas. Por ejemplo: 'Expertas en biotecnología', 'Investigadoras en energías renovables', 'Profesoras de medicina'.",
            class_name="text-sm text-gray-600 mb-3",
        ),
        rx.hstack(
            rx.hstack(
                rx.icon(
                    "sparkles",
                    size=20,
                    color="rgb(99, 102, 241)",
                    class_name="flex-shrink-0",
                ),
                optimized_ai_search_input(),
                spacing="3",
                style={
                    "flex": "1",
                    "background": "white",
                    "border": "2px solid rgb(229, 231, 235)",
                    "borderRadius": "12px",
                    "padding": "4px 16px",
                    "alignItems": "center",
                    "transition": "border-color 0.1s ease",  # Reducido para mejor UX
                    "contain": "layout style",  # Optimización de rendering
                },
                class_name="hover:border-indigo-300 focus-within:border-indigo-500 focus-within:shadow-lg",
            ),
            rx.button(
                rx.icon("search", size=18),
                "Buscar",
                on_click=State.perform_ai_search,
                size="3",
                color_scheme="indigo",
                variant="solid",
                style={
                    "padding": "12px 24px",
                    "fontWeight": "600",
                    "borderRadius": "12px",
                    "cursor": "pointer",
                },
                disabled=State.ai_search_loading,
                loading=State.ai_search_loading,  # Añadido estado de loading visual
            ),
            spacing="3",
            width="100%",
            align="center",
        ),
        rx.hstack(
            rx.icon("corner-down-left", size=14, color="rgb(156, 163, 175)"),
            rx.text(
                "Presiona Enter para buscar",
                class_name="text-xs text-gray-500",
            ),
            spacing="1",
            justify="start",
            class_name="ml-1",
        ),
        # Estado de loading optimizado con mejores transiciones
        rx.cond(
            State.ai_search_loading,
            rx.hstack(
                rx.spinner(size="2", color="indigo"),
                rx.text(
                    "Analizando tu consulta con IA...",
                    class_name="text-sm text-indigo-600 font-medium",
                ),
                spacing="2",
                align="center",
                class_name="mt-2 p-3 bg-indigo-50 rounded-lg border border-indigo-200 animate-in fade-in duration-200",
            ),
        ),
        # Resultados con mejor feedback visual
        rx.cond(
            State.ai_search_results_summary,
            rx.vstack(
                rx.divider(),
                rx.hstack(
                    rx.icon("brain-circuit", size=16, color="rgb(99, 102, 241)"),
                    rx.text(
                        "Resultados interpretados por IA:",
                        class_name="text-sm font-semibold text-indigo-700",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    State.ai_search_results_summary,
                    class_name="text-sm text-gray-700 p-3 bg-blue-50 rounded-lg border border-blue-200",
                ),
                spacing="2",
                width="100%",
                class_name="mt-3 animate-in slide-in-from-top duration-300",
            ),
        ),
        # Error feedback optimizado
        rx.cond(
            State.ai_search_error,
            rx.callout(
                State.ai_search_error,
                icon="triangle-alert",
                color_scheme="red",
                class_name="mt-2 animate-in fade-in duration-200",
            ),
        ),
        spacing="4",
        width="100%",
        class_name="bg-white shadow-lg rounded-xl p-6 border border-gray-100",
        style={
            "contain": "layout style",  # Mejora el rendimiento de rendering
        },
    )


def simple_ai_search_replace() -> rx.Component:
    """
    CERO renders mientras escribe - búsqueda solo bajo demanda.
    """
    return rx.hstack(
        rx.input(
            placeholder="Buscar con IA: 'investigadoras en biotecnología', 'expertas en energías renovables'...",
            value=State.ai_search_input,  # Solo texto visible
            on_change=State.set_ai_search_input,  # Solo actualiza texto
            on_key_down=State.handle_ai_search_enter,  # Busca con Enter
            size="3",
            # style={
            #     "flex": "1",
            #     "borderRadius": "8px",
            #     "transition": "border-color 0.05s ease",  # Ultra optimizado
            #     "contain": "layout style paint",
            # },
            # class_name="border-gray-300 focus:border-indigo-500 bg-neutral-300 text-indigo-900",
            # color_scheme="indigo",
            spell_check=False,
            color="black",
            class_name="w-full border-gray-300 border-indigo-500 focus:ring-2 focus:ring-indigo-200",
        ),
        rx.button(
            rx.icon("sparkles", size=16),
            "Buscar",
            on_click=State.perform_ai_search,  # Busca al hacer clic
            size="2",
            color_scheme="indigo",
            variant="solid",
            disabled=State.ai_search_loading,
            loading=State.ai_search_loading,
            style={
                "cursor": "pointer",
            },
        ),
        spacing="2",
        width="100%",
        align="center",
        style={
            "contain": "layout style",  # Optimización de rendering
        },
    )