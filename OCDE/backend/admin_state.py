"""
AdminState — CRUD de documentos para el panel administrativo.
Usa SQLite vía rx.session() y almacena archivos en assets/uploads/.
"""
import reflex as rx
import reflex_clerk as clerk
import asyncio
import logging
import shutil
from pathlib import Path
from datetime import datetime
from sqlmodel import select
from .models import Documento

logger = logging.getLogger(__name__)

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

# Ruta absoluta: OCDE/backend/admin_state.py → 3 niveles arriba = raíz del proyecto
_PROJECT_ROOT = Path(__file__).parent.parent.parent
UPLOADS_DIR = _PROJECT_ROOT / "assets" / "uploads"


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
    sync_status: str = ""
    is_syncing: bool = False

    pub_upload_status: str = ""
    is_uploading_pub: bool = False

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
        # Recargar el agente IA para que incluya el nuevo documento
        try:
            from .chatbot.pdf_agent import reload_pdf_chatbot
            await asyncio.to_thread(reload_pdf_chatbot)
            self.upload_status = "Subida exitosa. Chatbot actualizado con el nuevo documento."
        except Exception as e:
            logger.warning(f"Documento subido pero el chatbot no pudo recargarse: {e}")
            self.upload_status = f"Documento subido exitosamente, pero el chatbot no pudo recargarse: {e}"
        yield AdminState.load_documents

    @rx.event
    def delete_document(self, doc_id: int):
        with rx.session() as session:
            doc = session.get(Documento, doc_id)
            if doc:
                # filename puede ser "uploads/foo.pdf" o "foo.pdf" (datos semilla en assets/)
                filepath = _PROJECT_ROOT / "assets" / doc.filename
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

    @rx.event
    async def upload_publicaciones(self, files: list[rx.UploadFile]):
        """
        Reemplaza publicaciones_total.xlsx con el Excel subido por el admin
        y recarga el DataCache sin reiniciar el servidor.
        """
        if not files:
            self.pub_upload_status = "No se seleccionó ningún archivo."
            return

        file = files[0]
        filename = file.name or "publicaciones.xlsx"
        if not filename.lower().endswith((".xlsx", ".xls")):
            self.pub_upload_status = "❌ El archivo debe ser un Excel (.xlsx o .xls)"
            return

        self.is_uploading_pub = True
        self.pub_upload_status = "Procesando archivo..."
        yield

        import io
        import pandas as pd
        from pathlib import Path
        from datetime import datetime
        from .data_cache import DataCache, PUBLICACIONES_FILE

        try:
            # Leer bytes
            if file.path and file.path.exists():
                data = await asyncio.to_thread(file.path.read_bytes)
            else:
                data = await file.read()

            # Validar columna mínima requerida
            df_nuevo = await asyncio.to_thread(pd.read_excel, io.BytesIO(data))
            if "rut_ir" not in df_nuevo.columns:
                self.pub_upload_status = (
                    f"❌ Columna 'rut_ir' no encontrada. "
                    f"Columnas detectadas: {', '.join(df_nuevo.columns.tolist())}"
                )
                self.is_uploading_pub = False
                return

            # Determinar ruta de destino (misma que lee DataCache)
            output_path = Path(DataCache._data_directory) / PUBLICACIONES_FILE

            # Backup del archivo anterior si existe
            if output_path.exists():
                backup = output_path.with_name(
                    f"publicaciones_total_backup_{datetime.now():%Y%m%d_%H%M}.xlsx"
                )
                await asyncio.to_thread(output_path.rename, backup)

            # Guardar nuevo archivo
            await asyncio.to_thread(_write_bytes, output_path, data)

            # Recargar DataCache
            total = await asyncio.to_thread(DataCache.reload_publicaciones)
            self.pub_upload_status = (
                f"✅ {total} publicaciones cargadas desde '{filename}'"
            )

        except Exception as e:
            self.pub_upload_status = f"❌ Error: {e}"
        finally:
            self.is_uploading_pub = False

    @rx.event
    async def sincronizar_publicaciones(self):
        """Ejecuta el script de sync en segundo plano y recarga el DataCache."""
        import subprocess
        import sys
        from pathlib import Path

        self.is_syncing = True
        self.sync_status = "Sincronizando publicaciones..."
        yield

        script = Path(__file__).parent.parent.parent / "scripts" / "sync_publicaciones.py"
        if not script.exists():
            self.sync_status = f"Error: script no encontrado en {script}"
            self.is_syncing = False
            return

        try:
            result = await asyncio.to_thread(
                subprocess.run,
                [sys.executable, str(script)],
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode == 0:
                # Recargar DataCache sin reiniciar servidor
                from .data_cache import DataCache
                total = await asyncio.to_thread(DataCache.reload_publicaciones)
                self.sync_status = f"✅ Sync completada — {total} publicaciones cargadas"
            else:
                self.sync_status = f"❌ Error en sync: {result.stderr[-300:]}"
        except subprocess.TimeoutExpired:
            self.sync_status = "❌ Timeout: el scraper tardó más de 10 min"
        except Exception as e:
            self.sync_status = f"❌ Error inesperado: {e}"
        finally:
            self.is_syncing = False
