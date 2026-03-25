"""
Panel administrativo protegido por Clerk.
Permite subir, editar y eliminar reportes/documentos del repositorio.
"""
import os
import reflex as rx
import reflex_clerk as clerk
from ..backend.admin_state import AdminState, AdminAuthState
from .searchbar import navbar_searchbar_notsearch


# =========================================================
# DIÁLOGO DE EDICIÓN (global, fuera del foreach)
# =========================================================

def edit_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Editar documento"),
            rx.vstack(
                rx.text("Título", size="2", weight="bold"),
                rx.input(
                    value=AdminState.edit_titulo,
                    on_change=AdminState.set_edit_titulo,
                    placeholder="Título del documento",
                    width="100%",
                ),
                rx.text("Descripción", size="2", weight="bold"),
                rx.text_area(
                    value=AdminState.edit_descripcion,
                    on_change=AdminState.set_edit_descripcion,
                    placeholder="Descripción o fuente",
                    width="100%",
                    rows="3",
                ),
                rx.hstack(
                    rx.button(
                        "Guardar",
                        on_click=AdminState.save_edit,
                        color_scheme="indigo",
                    ),
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray"),
                    ),
                    spacing="3",
                ),
                spacing="3",
                width="100%",
            ),
            max_width="500px",
        ),
        open=AdminState.edit_dialog_open,
        on_open_change=AdminState.set_edit_dialog_open,
    )


# =========================================================
# FORMULARIO DE SUBIDA
# =========================================================

def upload_form() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Subir nuevo documento", size="5", class_name="text-indigo-700"),
            rx.vstack(
                rx.text("Título *", size="2", weight="bold"),
                rx.input(
                    value=AdminState.upload_titulo,
                    on_change=AdminState.set_upload_titulo,
                    placeholder="Ej: Reporte General 2025",
                    width="100%",
                ),
                rx.text("Descripción / Fuente", size="2", weight="bold"),
                rx.input(
                    value=AdminState.upload_descripcion,
                    on_change=AdminState.set_upload_descripcion,
                    placeholder="Ej: UFRO, 2025",
                    width="100%",
                ),
                rx.text("Tipo", size="2", weight="bold"),
                rx.select.root(
                    rx.select.trigger(placeholder="Seleccionar tipo"),
                    rx.select.content(
                        rx.select.item("Reporte", value="reporte"),
                        rx.select.item("Documento", value="documento"),
                    ),
                    value=AdminState.upload_tipo,
                    on_change=AdminState.set_upload_tipo,
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            rx.upload(
                rx.vstack(
                    rx.icon("upload", size=32, class_name="text-indigo-400"),
                    rx.text(
                        "Arrastra un PDF aquí o haz clic para seleccionar",
                        size="2",
                        class_name="text-gray-500 text-center",
                    ),
                    rx.text(
                        rx.selected_files("pdf_upload"),
                        size="1",
                        class_name="text-indigo-600",
                    ),
                    spacing="2",
                    align="center",
                ),
                id="pdf_upload",
                accept={"application/pdf": [".pdf"]},
                max_files=1,
                class_name="border-2 border-dashed border-indigo-300 rounded-lg p-6 w-full cursor-pointer hover:border-indigo-500 transition-colors",
            ),
            rx.button(
                rx.cond(
                    AdminState.is_uploading,
                    rx.hstack(
                        rx.spinner(size="2"),
                        rx.text("Subiendo..."),
                        spacing="2",
                    ),
                    rx.text("Subir PDF"),
                ),
                on_click=AdminState.handle_upload(
                    rx.upload_files(upload_id="pdf_upload")
                ),
                disabled=AdminState.is_uploading,
                color_scheme="indigo",
                width="100%",
            ),
            rx.cond(
                AdminState.upload_status != "",
                rx.callout(
                    AdminState.upload_status,
                    icon=rx.cond(
                        AdminState.upload_status.contains("exitosa"),
                        "check",
                        "info",
                    ),
                    color_scheme=rx.cond(
                        AdminState.upload_status.contains("exitosa"),
                        "green",
                        "tomato",
                    ),
                ),
            ),
            spacing="4",
            width="100%",
        ),
        class_name="w-full max-w-2xl",
    )


# =========================================================
# FILA DE DOCUMENTO EN LA LISTA
# =========================================================

def _admin_doc_row(item: dict) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(item["titulo"], weight="bold", size="3", class_name="text-indigo-800"),
                rx.text(item["descripcion"], size="2", class_name="text-gray-500"),
                rx.hstack(
                    rx.badge(item["tipo"], color_scheme="indigo", variant="soft"),
                    rx.text(item["created_at"], size="1", class_name="text-gray-400"),
                    spacing="2",
                    align="center",
                ),
                spacing="1",
                flex="1",
            ),
            rx.hstack(
                rx.button(
                    rx.icon("pencil", size=14),
                    "Editar",
                    size="2",
                    variant="soft",
                    color_scheme="indigo",
                    on_click=AdminState.start_edit(
                        item["id"], item["titulo"], item["descripcion"]
                    ),
                ),
                rx.button(
                    rx.icon("trash-2", size=14),
                    "Eliminar",
                    size="2",
                    variant="soft",
                    color_scheme="red",
                    on_click=AdminState.delete_document(item["id"]),
                ),
                spacing="2",
            ),
            align="center",
            spacing="4",
            width="100%",
        ),
        class_name="w-full",
    )


def documents_list(items, label: str) -> rx.Component:
    return rx.vstack(
        rx.cond(
            items.length() == 0,
            rx.callout(
                f"No hay {label} cargados aún. Usa el formulario para subir el primero.",
                icon="info",
                color_scheme="gray",
                class_name="w-full",
            ),
            rx.foreach(items, _admin_doc_row),
        ),
        spacing="3",
        width="100%",
    )


# =========================================================
# CONTENIDO ADMIN (firmado)
# =========================================================

def admin_content() -> rx.Component:
    return rx.vstack(
        edit_dialog(),
        navbar_searchbar_notsearch(),
        rx.vstack(
            rx.hstack(
                rx.icon("shield-check", size=28, class_name="text-indigo-600"),
                rx.heading("Panel Administrativo", size="6", class_name="text-indigo-800"),
                rx.spacer(),
                clerk.user_button(),
                align="center",
                width="100%",
                spacing="3",
            ),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Subir nuevo", value="upload"),
                    rx.tabs.trigger("Reportes", value="reportes"),
                    rx.tabs.trigger("Documentos", value="documentos"),
                ),
                rx.tabs.content(
                    upload_form(),
                    value="upload",
                    class_name="py-4",
                ),
                rx.tabs.content(
                    documents_list(AdminState.reportes_admin, "reportes"),
                    value="reportes",
                    class_name="py-4",
                ),
                rx.tabs.content(
                    documents_list(AdminState.documentos_admin, "documentos"),
                    value="documentos",
                    class_name="py-4",
                ),
                default_value="upload",
                width="100%",
            ),
            class_name="w-full max-w-4xl mx-auto p-6",
            spacing="4",
        ),
        width="100%",
        spacing="0",
    )


# =========================================================
# VISTA DE ACCESO NO AUTORIZADO
# =========================================================

def unauthorized_view() -> rx.Component:
    return rx.flex(
        rx.vstack(
            rx.icon("shield-x", size=48, class_name="text-red-400"),
            rx.heading("Acceso no autorizado", size="6", class_name="text-red-700"),
            rx.text(
                "Tu cuenta no tiene permiso para acceder al panel administrativo.",
                class_name="text-gray-500 text-center",
            ),
            clerk.sign_out_button(
                rx.button(
                    "Cerrar sesión",
                    color_scheme="red",
                    variant="soft",
                    size="3",
                ),
            ),
            spacing="4",
            align="center",
        ),
        justify="center",
        align="center",
        min_height="100vh",
        width="100%",
        class_name="bg-gray-50",
    )


# =========================================================
# PÁGINA ADMIN PRINCIPAL
# =========================================================

def admin_page() -> rx.Component:
    return clerk.clerk_provider(
        clerk.signed_in(
            rx.cond(
                AdminAuthState.is_authorized,
                admin_content(),
                unauthorized_view(),
            ),
        ),
        clerk.signed_out(
            rx.flex(
                rx.vstack(
                    rx.heading("Panel Administrativo", size="6", class_name="text-indigo-800"),
                    rx.text("Inicia sesión para acceder.", class_name="text-gray-500"),
                    clerk.sign_in(),
                    spacing="4",
                    align="center",
                ),
                justify="center",
                align="center",
                min_height="100vh",
                width="100%",
                class_name="bg-gray-50",
            ),
        ),
        publishable_key=os.environ.get("CLERK_PUBLISHABLE_KEY", ""),
        secret_key=os.environ.get("CLERK_SECRET_KEY", ""),
    )
