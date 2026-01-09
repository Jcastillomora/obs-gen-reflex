import reflex as rx
from ..backend.backend import State


def render_message_bubble(msg):
    """Renderiza una burbuja de mensaje con el diseño correspondiente según el rol."""
    return rx.cond(
        msg["role"] == "assistant",
        rx.box(
            rx.hstack(
                rx.box(
                    rx.icon("sparkle", size=18),
                    class_name="bg-[#2563eb] p-2 rounded-full shadow-sm",
                    style={
                        "color": "white",
                        "min_width": "36px",
                        "height": "36px",
                        "flex_shrink": "0",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                    },
                ),
                rx.box(
                    rx.markdown(
                        msg["content"],
                        style={
                            "color": "#1e293b",
                            "line_height": "1.6",
                            "font_size": "14px",
                            "font_family": "system-ui, -apple-system, sans-serif",
                        },
                    ),
                    class_name="bg-white border border-[#e2e8f0] rounded-xl rounded-tl-lg p-4 shadow-sm",
                    style={
                        "word_wrap": "break_word",
                        "max_width": "75%",
                    },
                ),
                align_items="flex-start",
                spacing="3",
                justify_content="flex-start",
            ),
            width="100%",
            class_name="mb-4",
        ),
        rx.box(
            rx.hstack(
                rx.box(
                    rx.text(
                        msg["content"],
                        style={
                            "color": "white",
                            "line_height": "1.6",
                            "font_size": "14px",
                            "font_family": "system-ui, -apple-system, sans-serif",
                        },
                    ),
                    class_name="bg-[#3b82f6] rounded-xl rounded-tr-lg p-4 shadow-sm",
                    style={
                        "word_wrap": "break_word",
                        "max_width": "75%",
                    },
                ),
                rx.box(
                    rx.icon("user", size=18),
                    class_name="bg-[#64748b] p-2 rounded-full shadow-sm",
                    style={
                        "color": "white",
                        "min_width": "36px",
                        "height": "36px",
                        "flex_shrink": "0",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                    },
                ),
                align_items="flex-start",
                spacing="3",
                justify_content="flex-end",
            ),
            width="100%",
            class_name="mb-4",
        ),
    )


def loading_bubble():
    """Burbuja de loading para mostrar cuando el asistente está procesando."""
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon("sparkle", size=18),
                class_name="bg-[#2563eb] p-2 rounded-full shadow-sm",
                style={
                    "color": "white",
                    "min_width": "36px",
                    "height": "36px",
                    "flex_shrink": "0",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                },
            ),
            rx.box(
                rx.hstack(
                    rx.spinner(size="3", color="#3b82f6"),
                    rx.text(
                        "Escribiendo...",
                        style={
                            "color": "#64748b",
                            "font_size": "14px",
                            "font_style": "italic",
                        },
                    ),
                    align_items="center",
                    spacing="3",
                ),
                class_name="bg-[#f8fafc] border border-[#e2e8f0] rounded-xl rounded-tl-lg p-4 shadow-sm",
                style={"animation": "pulse 2s infinite"},
            ),
            align_items="flex-start",
            spacing="3",
            justify_content="flex-start",
        ),
        width="100%",
        class_name="mb-4",
    )


def chatbot_assistant():
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("sparkle", size=28),
                    class_name="bg-gradient-to-br from-[#3b82f6] to-[#2563eb] p-3 rounded-full shadow-lg",
                    style={
                        "color": "white",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                    },
                ),
                rx.vstack(
                    rx.heading(
                        "Asistente Inteligente",
                        size="6",
                        weight="bold",
                        style={
                            "color": "#1e293b",
                            "font_family": "system-ui, -apple-system, sans-serif",
                        },
                    ),
                    rx.text(
                        "Pregúntame sobre reportes y documentos disponibles en esta sección",
                        size="3",
                        style={
                            "color": "#64748b",
                            "line_height": "1.5",
                            "font_family": "system-ui, -apple-system, sans-serif",
                        },
                    ),
                    spacing="1",
                    align_items="flex-start",
                ),
                align_items="center",
                spacing="4",
            ),
            rx.box(
                rx.vstack(
                    rx.foreach(
                        State.chatbot_messages,
                        render_message_bubble,
                    ),
                    rx.cond(
                        State.chatbot_is_loading,
                        loading_bubble(),
                    ),
                    spacing="2",
                    width="100%",
                    style={"padding": "8px"},
                ),
                class_name="bg-gradient-to-b from-[#f8fafc] to-[#f1f5f9] rounded-xl border border-[#e2e8f0]",
                style={
                    "min_height": "450px",
                    "max_height": "550px",
                    "overflow_y": "auto",
                    "scroll_behavior": "smooth",
                    "scrollbar_width": "thin",
                },
                width="100%",
                id="chatbot-messages",
            ),
            rx.hstack(
                rx.input(
                    placeholder="Escribe tu pregunta aquí...",
                    value=State.chatbot_input,
                    on_change=State.set_chatbot_input,
                    on_key_down=State.handle_chatbot_key_press,
                    class_name="flex-1",
                    style={
                        "color": "#1e293b",
                        "border": "2px solid #e2e8f0",
                        "border_radius": "12px",
                        "padding": "14px 16px",
                        "background": "white",
                        "height": "52px",
                        "font_size": "14px",
                        "font_family": "system-ui, -apple-system, sans-serif",
                        "transition": "all 0.2s ease",
                        "box_shadow": "0 1px 3px rgba(0, 0, 0, 0.1)",
                        "_focus": {
                            "border_color": "#3b82f6",
                            "box_shadow": "0 0 0 3px rgba(59, 130, 246, 0.1)",
                            "outline": "none",
                        },
                    },
                    disabled=State.chatbot_is_loading,
                ),
                rx.button(
                    rx.cond(
                        State.chatbot_is_loading,
                        rx.spinner(size="3", color="white"),
                        rx.icon("send", size=18),
                    ),
                    on_click=State.send_user_message_immediate,
                    disabled=(State.chatbot_input == "") | State.chatbot_is_loading,
                    class_name="bg-gradient-to-br from-[#3b82f6] to-[#2563eb] hover:from-[#2563eb] hover:to-[#1d4ed8] text-white rounded-xl shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200",
                    style={
                        "min_width": "52px",
                        "height": "52px",
                        "border": "none",
                        "_hover": {
                            "transform": "translateY(-1px)",
                            "box_shadow": "0 4px 12px rgba(59, 130, 246, 0.4)",
                        },
                    },
                ),
                spacing="3",
                width="100%",
            ),
            rx.cond(
                State.chatbot_error != "",
                rx.box(
                    rx.hstack(
                        rx.icon("triangle_alert", size=16, color="#ef4444"),
                        rx.text(
                            State.chatbot_error,
                            style={
                                "color": "#ef4444",
                                "font_size": "13px",
                                "font_family": "system-ui, -apple-system, sans-serif",
                            },
                        ),
                        align_items="center",
                        spacing="2",
                    ),
                    class_name="bg-[#fef2f2] border border-[#fecaca] rounded-lg p-3",
                ),
            ),
            spacing="5",
            width="100%",
        ),
        width="100%",
        class_name="bg-white rounded-2xl border border-[#e2e8f0] p-6 shadow-xl",
        style={
            "background": "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)",
        },
        on_mount=State.initialize_chatbot,
    )