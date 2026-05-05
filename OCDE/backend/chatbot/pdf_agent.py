import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
import pypdf
from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent
from agno.models.anthropic import Claude

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _read_pdf_text(pdf_path: Path) -> str:
    """Lee el texto de un PDF usando pypdf directamente."""
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n\n".join(pages_text)
    except Exception as e:
        logger.error(f"Error leyendo PDF {pdf_path.name} con pypdf: {e}")
        return ""


class SimpleDocument:
    """Clase simple para documentos con metadata."""

    def __init__(self, content: str, file_name: str, file_type: str):
        self.content = content
        self.file_name = file_name
        self.file_type = file_type


# Ruta absoluta a assets/: pdf_agent.py → chatbot/ → backend/ → OCDE/ → raíz proyecto
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
_ASSETS_DIR = _PROJECT_ROOT / "assets"
_UPLOADS_DIR = _ASSETS_DIR / "uploads"


class AgnoDocumentChatbot:
    """
    Chatbot usando Agno framework con Agent y Claude para PDFs y Excel.
    """

    def __init__(self):
        self.agent: Optional[Agent] = None
        self.documents = []
        self._initialize()

    def _initialize(self):
        """Inicializa Agno Agent con PDFReader, Excel reader y Claude."""
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY no configurada")
                return

            self._load_documents()

            if not self.documents:
                logger.warning("No se encontraron documentos válidos")
                return

            context = self._create_context()

            # Crear Agent con Claude
            self.agent = Agent(
                model=Claude(id="claude-haiku-4-5-20251001"),
                instructions=f"""Eres un asistente inteligente especializado en el Observatorio de Género en Ciencia de la Universidad de La Frontera (UFRO).

CONTEXTO DE DOCUMENTOS:
{context}

REGLAS IMPORTANTES:
1. Solo responde con información que esté explícitamente en los documentos proporcionados
2. Si no encuentras la información en los documentos, di claramente que no tienes esa información
3. Responde siempre en español
4. Sé conciso pero completo
5. NUNCA menciones nombres específicos de archivos (como "academicas.xlsx", "Reporte.pdf", etc.). En su lugar usa referencias genéricas como "Según los datos académicos de la UFRO" o "Basándome en la información del observatorio"
6. No inventes información que no esté en los documentos
7. Puedes responder preguntas sobre datos de archivos Excel y PDFs

PRIVACIDAD Y CONFIDENCIALIDAD:
- NUNCA proporciones RUTs, cédulas de identidad, o números de identificación personal
- Si te preguntan por RUTs o información confidencial, responde que esa información está protegida por privacidad
- Los archivos Excel han sido filtrados automáticamente para excluir datos confidenciales
- Enfócate en información académica no sensible: nombres, áreas de investigación, publicaciones, proyectos""",
                description="Asistente del Observatorio OCDE especializado en documentos PDF y Excel",
            )

            logger.info("Agno Agent inicializado correctamente con Claude")

        except Exception as e:
            logger.error(f"Error inicializando Agno Agent: {e}")

    def _load_documents(self):
        """Carga documentos PDF y Excel desde assets/ y assets/uploads/."""
        try:
            logger.info(f"Buscando documentos en: {_ASSETS_DIR} y {_UPLOADS_DIR}")

            if not _ASSETS_DIR.exists():
                logger.warning(f"Directorio assets/ no existe: {_ASSETS_DIR}")
                return

            # PDFs en assets/ y en assets/uploads/
            pdf_files = list(_ASSETS_DIR.glob("*.pdf"))
            if _UPLOADS_DIR.exists():
                pdf_files += list(_UPLOADS_DIR.glob("*.pdf"))

            # Excel solo en assets/ raíz (archivos de datos)
            excel_files = list(_ASSETS_DIR.glob("*.xlsx")) + list(_ASSETS_DIR.glob("*.xls"))

            logger.info(
                f"Encontrados: {len(pdf_files)} PDFs, {len(excel_files)} Excel "
                f"(uploads dir existe: {_UPLOADS_DIR.exists()})"
            )

            if not pdf_files and not excel_files:
                logger.warning(f"No se encontraron documentos en {_ASSETS_DIR}")
                return

            if pdf_files:
                for pdf_file in pdf_files:
                    try:
                        logger.info(f"Cargando PDF: {pdf_file.name}")
                        text = _read_pdf_text(pdf_file)
                        if text.strip():
                            wrapped_doc = SimpleDocument(
                                content=f"ARCHIVO PDF: {pdf_file.name}\n\n{text}",
                                file_name=pdf_file.name,
                                file_type="PDF",
                            )
                            self.documents.append(wrapped_doc)
                            logger.info(f"PDF cargado exitosamente: {pdf_file.name} ({len(text)} caracteres)")
                        else:
                            logger.warning(f"PDF sin texto extraíble (posiblemente imagen): {pdf_file.name}")
                    except Exception as e:
                        logger.error(f"Error leyendo PDF {pdf_file.name}: {e}")

            # Procesar archivos Excel
            if excel_files:
                for excel_file in excel_files:
                    try:
                        logger.info(f"Cargando Excel: {excel_file.name}")
                        excel_content = self._read_excel_file(excel_file)
                        if excel_content:
                            excel_doc = SimpleDocument(
                                content=excel_content,
                                file_name=excel_file.name,
                                file_type="Excel",
                            )
                            self.documents.append(excel_doc)
                    except Exception as e:
                        logger.error(f"Error leyendo Excel {excel_file.name}: {e}")

            logger.info(
                f"Cargados {len(self.documents)} documentos exitosamente "
                f"({len(pdf_files)} PDFs, {len(excel_files)} Excel)"
            )

        except Exception as e:
            logger.error(f"Error cargando documentos: {e}")

    def _read_excel_file(self, excel_file: Path) -> Optional[str]:
        """Lee un archivo Excel y lo convierte a texto, filtrando información confidencial."""
        try:
            CONFIDENTIAL_COLUMNS = [
                "rut",
                "rut_ir",
                "rut_academica",
                "cedula",
                "ci",
                "dni",
                "password",
                "contraseña",
                "clave",
                "token",
                "api_key",
            ]

            excel_data = pd.read_excel(excel_file, sheet_name=None)

            content_parts = [f"ARCHIVO EXCEL: {excel_file.name}\n"]
            content_parts.append(
                "NOTA: Información confidencial (RUTs, etc.) ha sido filtrada por privacidad.\n"
            )

            for sheet_name, df in excel_data.items():
                if df.empty:
                    continue

                # Filtrar columnas confidenciales
                original_columns = list(df.columns)
                safe_columns = []
                filtered_columns = []

                for col in df.columns:
                    col_lower = str(col).lower()
                    if any(
                        conf_col.lower() in col_lower
                        for conf_col in CONFIDENTIAL_COLUMNS
                    ):
                        filtered_columns.append(col)
                    else:
                        safe_columns.append(col)

                if safe_columns:
                    df_safe = df[safe_columns]
                else:
                    df_safe = pd.DataFrame(
                        {
                            "info": [
                                f"Archivo con {len(df)} registros - columnas filtradas por privacidad"
                            ]
                        }
                    )

                content_parts.append(f"\n--- HOJA: {sheet_name} ---")

                if filtered_columns:
                    content_parts.append(
                        f"Columnas filtradas por privacidad: {', '.join(filtered_columns)}"
                    )

                if not df_safe.empty:
                    content_parts.append(
                        f"Filas: {len(df)}, Columnas disponibles: {len(df_safe.columns)}"
                    )
                    content_parts.append(
                        f"Columnas disponibles: {', '.join(str(col) for col in df_safe.columns)}"
                    )

                    sample_size = min(10, len(df_safe))
                    if sample_size > 0:
                        content_parts.append(
                            f"\nPrimeras {sample_size} filas (datos no confidenciales):"
                        )

                        for idx in range(sample_size):
                            row = df_safe.iloc[idx]
                            row_data = []
                            for col in df_safe.columns:
                                value = row[col]
                                if pd.isna(value):
                                    value = "N/A"
                                row_data.append(f"{col}: {value}")
                            content_parts.append(
                                f"Fila {idx + 1}: {' | '.join(row_data)}"
                            )

                    numeric_cols = df_safe.select_dtypes(include=["number"]).columns
                    if len(numeric_cols) > 0:
                        content_parts.append(f"\nEstadísticas columnas numéricas:")
                        for col in numeric_cols:
                            try:
                                serie = df_safe[col]
                                promedio = serie.mean()
                                minimo = serie.min()
                                maximo = serie.max()
                                content_parts.append(
                                    f"{col}: Promedio={promedio:.2f}, "
                                    f"Min={minimo:.2f}, Max={maximo:.2f}"
                                )
                            except Exception as e:
                                content_parts.append(
                                    f"{col}: Error calculando estadísticas"
                                )

            return "\n".join(content_parts)

        except Exception as e:
            logger.error(f"Error procesando Excel {excel_file.name}: {e}")
            return None

    def _create_context(self) -> str:
        """Crea contexto con todos los documentos disponibles."""
        if not self.documents:
            return ""

        context_parts = []
        total_length = 0
        # Claude Haiku tiene ventana de 200k tokens (~800k chars).
        # Usamos 400k como límite seguro para dejar espacio a instrucciones y respuesta.
        max_context_length = 400_000

        for doc in self.documents:
            file_name = getattr(doc, "file_name", "Desconocido")
            file_type = getattr(doc, "file_type", "Desconocido")

            doc_content = f"\n\n=== DOCUMENTO: {file_name} (Tipo: {file_type}) ===\n{doc.content}\n"

            if total_length + len(doc_content) > max_context_length:
                logger.warning(
                    f"Contexto lleno ({total_length:,} chars). "
                    f"Omitiendo: {file_name} ({len(doc_content):,} chars)"
                )
                break

            context_parts.append(doc_content)
            total_length += len(doc_content)

        logger.info(f"Contexto generado: {total_length:,} chars con {len(context_parts)} documentos")
        return "".join(context_parts)

    def is_ready(self) -> bool:
        """Verifica si el agent está listo para responder."""
        return self.agent is not None and len(self.documents) > 0

    def ask(self, question: str) -> str:
        """
        Hace una pregunta al agent usando Agno.

        Args:
            question: Pregunta del usuario

        Returns:
            Respuesta del agent
        """
        try:
            if not self.is_ready():
                return "El chatbot no está disponible. Verifique ANTHROPIC_API_KEY y documentos."

            if not question.strip():
                return "Por favor, haz una pregunta específica sobre los documentos del observatorio."

            if self.agent is not None:
                response = self.agent.run(question, add_history_to_messages=False)
            else:
                return "El agente no está inicializado correctamente."

            if hasattr(response, "content"):
                return str(response.content)
            else:
                return str(response)

        except Exception as e:
            logger.error(f"Error procesando pregunta con Agno: {e}")
            return f"Error al procesar tu pregunta: {str(e)}"

    def get_available_documents(self) -> List[str]:
        """Obtiene la lista de documentos disponibles."""
        documents = []
        if _ASSETS_DIR.exists():
            documents.extend([f.name for f in _ASSETS_DIR.glob("*.pdf")])
            documents.extend([f.name for f in _ASSETS_DIR.glob("*.xlsx")])
            documents.extend([f.name for f in _ASSETS_DIR.glob("*.xls")])
        if _UPLOADS_DIR.exists():
            documents.extend([f.name for f in _UPLOADS_DIR.glob("*.pdf")])
        return documents

    def reload(self):
        """Recarga documentos y recrea el agente (usar tras subir nuevos archivos)."""
        old_documents = self.documents[:]
        old_agent = self.agent
        try:
            self.documents = []
            self.agent = None
            self._initialize()
            if self.agent is None:
                # Restaurar estado anterior si el reload falló
                self.documents = old_documents
                self.agent = old_agent
                raise RuntimeError(
                    f"No se pudo inicializar el agente. "
                    f"Documentos encontrados: {len(self.documents)}. "
                    f"Verifica ANTHROPIC_API_KEY y que los PDFs tengan texto extraíble."
                )
            logger.info(
                f"Agno Agent recargado con {len(self.documents)} documentos actualizados"
            )
        except RuntimeError:
            raise
        except Exception as e:
            # Restaurar estado anterior ante cualquier error inesperado
            self.documents = old_documents
            self.agent = old_agent
            raise RuntimeError(f"Error durante el reload del chatbot: {e}") from e

    def get_agent_info(self) -> Dict[str, Any]:
        """Obtiene información sobre el estado del agent."""
        return {
            "ready": self.is_ready(),
            "assets_dir": str(_ASSETS_DIR),
            "uploads_dir": str(_UPLOADS_DIR),
            "available_documents": self.get_available_documents(),
            "model": "Claude Haiku 4.5 (via Agno)",
            "documents_loaded": len(self.documents),
            "framework": "Agno",
            "supports_pdf": True,
            "supports_excel": True,
            "uses_semantic_search": False,
        }


# Instancia global
agno_chatbot = AgnoDocumentChatbot()


def reload_pdf_chatbot() -> None:
    """Recarga el chatbot con los documentos actuales (llamar tras subir nuevos archivos)."""
    agno_chatbot.reload()


def get_pdf_chatbot_response(question: str) -> str:
    """Función de utilidad para obtener respuesta del chatbot Agno."""
    return agno_chatbot.ask(question)


def is_pdf_chatbot_ready() -> bool:
    """Función de utilidad para verificar si el chatbot Agno está listo."""
    return agno_chatbot.is_ready()


def get_pdf_chatbot_info() -> Dict[str, Any]:
    """Función de utilidad para obtener información del chatbot Agno."""
    return agno_chatbot.get_agent_info()


if __name__ == "__main__":
    print("=== Document Chatbot con Agno Framework (PDF + Excel) ===")
    print("Información del chatbot:")
    info = get_pdf_chatbot_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    if is_pdf_chatbot_ready():
        print("\n¡Chatbot Agno listo! Puedes hacer preguntas sobre PDFs y Excel.")

        # Pregunta de prueba
        test_question = "¿Qué información hay disponible en los documentos?"
        print(f"\nPregunta de prueba: {test_question}")
        response = get_pdf_chatbot_response(test_question)
        print(f"Respuesta: {response[:200]}...")
    else:
        print("\nChatbot Agno no está listo. Verifica la configuración.")