"""
AdminState — CRUD de documentos para el panel administrativo.
Usa SQLite vía rx.session() y almacena archivos en assets/uploads/.
"""
import reflex as rx
import reflex_clerk as clerk
import asyncio
import shutil
from pathlib import Path
from datetime import datetime
from sqlmodel import select
from .models import Documento

# Únicos emails autorizados para el panel de administración
ALLOWED_ADMIN_EMAILS = {
    "jorge.castillo@ufrontera.cl",
    "genero.ciencia@ufrontera.cl",
}


class AdminAuthState(clerk.ClerkState):
    """Estado de autorización: verifica que el email del usuario esté en la lista blanca."""

    @rx.var
    def is_authorized(self) -> bool:
        if not self.user or not self.user.email_addresses:
            return False
        for email_obj in self.user.email_addresses:
            if email_obj.email_address in ALLOWED_ADMIN_EMAILS:
                return True
        return False

UPLOADS_DIR = Path("assets/uploads")


def _write_bytes(path: Path, data: bytes) -> None:
    path.write_bytes(data)


class AdminState(rx.State):
    # Lista de todos los documentos cargados de DB (como dicts para serialización)
    documentos: list[dict] = []

    # Campos del formulario de subida
    upload_titulo: str = ""
    upload_descripcion: str = ""
    upload_tipo: str = "reporte"

    # Campos de edición inline
    edit_id: int = 0
    edit_titulo: str = ""
    edit_descripcion: str = ""
    edit_dialog_open: bool = False

    is_uploading: bool = False
    upload_status: str = ""

    # =========================================================
    # COMPUTED VARS
    # =========================================================

    @rx.var
    def reportes_admin(self) -> list[dict]:
        return [d for d in self.documentos if d.get("tipo") == "reporte"]

    @rx.var
    def documentos_admin(self) -> list[dict]:
        return [d for d in self.documentos if d.get("tipo") == "documento"]

    # =========================================================
    # EVENT HANDLERS
    # =========================================================

    @rx.event
    def load_documents(self):
        with rx.session() as session:
            docs = session.exec(select(Documento)).all()
            self.documentos = [
                {
                    "id": doc.id,
                    "titulo": doc.titulo,
                    "descripcion": doc.descripcion,
                    "tipo": doc.tipo,
                    "filename": doc.filename,
                    "created_at": doc.created_at,
                }
                for doc in docs
            ]

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            self.upload_status = "No se seleccionó ningún archivo."
            return
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        self.is_uploading = True
        self.upload_status = ""
        for file in files:
            # Reflex 0.8.x usa .name (no .filename); el archivo ya está en file.path
            filename = file.name or (file.path.name if file.path else "uploaded.pdf")
            filepath = UPLOADS_DIR / filename
            if file.path and file.path.exists():
                await asyncio.to_thread(shutil.copy, file.path, filepath)
            else:
                data = await file.read()
                await asyncio.to_thread(_write_bytes, filepath, data)
            with rx.session() as session:
                doc = Documento(
                    titulo=self.upload_titulo or filename,
                    descripcion=self.upload_descripcion,
                    tipo=self.upload_tipo,
                    filename=f"uploads/{filename}",   # URL pública: /uploads/filename
                    created_at=datetime.now().strftime("%Y-%m-%d"),
                )
                session.add(doc)
                session.commit()
        self.is_uploading = False
        self.upload_titulo = ""
        self.upload_descripcion = ""
        self.upload_status = "Documento subido exitosamente."
        # Recargar el agente IA para que incluya el nuevo documento
        try:
            from .chatbot.pdf_agent import reload_pdf_chatbot
            await asyncio.to_thread(reload_pdf_chatbot)
        except Exception:
            pass
        yield AdminState.load_documents

    @rx.event
    def delete_document(self, doc_id: int):
        with rx.session() as session:
            doc = session.get(Documento, doc_id)
            if doc:
                # filename puede ser "uploads/foo.pdf" o "foo.pdf" (datos semilla en assets/)
                filepath = Path("assets") / doc.filename
                if filepath.exists():
                    filepath.unlink()
                session.delete(doc)
                session.commit()
        yield AdminState.load_documents

    @rx.event
    def start_edit(self, doc_id: int, titulo: str, descripcion: str):
        self.edit_id = doc_id
        self.edit_titulo = titulo
        self.edit_descripcion = descripcion
        self.edit_dialog_open = True

    @rx.event
    def save_edit(self):
        with rx.session() as session:
            doc = session.get(Documento, self.edit_id)
            if doc:
                doc.titulo = self.edit_titulo
                doc.descripcion = self.edit_descripcion
                session.add(doc)
                session.commit()
        self.edit_dialog_open = False
        yield AdminState.load_documents

    @rx.event
    def set_edit_dialog_open(self, value: bool):
        self.edit_dialog_open = value

    @rx.event
    def set_upload_titulo(self, value: str):
        self.upload_titulo = value

    @rx.event
    def set_upload_descripcion(self, value: str):
        self.upload_descripcion = value

    @rx.event
    def set_upload_tipo(self, value: str):
        self.upload_tipo = value

    @rx.event
    def set_edit_titulo(self, value: str):
        self.edit_titulo = value

    @rx.event
    def set_edit_descripcion(self, value: str):
        self.edit_descripcion = value
