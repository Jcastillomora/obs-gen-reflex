import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.knowledge.reader.pdf_reader import PDFReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleDocument:
    """Clase simple para documentos con metadata."""

    def __init__(self, content: str, file_name: str, file_type: str):
        self.content = content
        self.file_name = file_name
        self.file_type = file_type


class AgnoDocumentChatbot:
    """
    Chatbot usando Agno framework con Agent, PDFReader y Claude para PDFs y Excel.
    """

    def __init__(self, documents_directory: str = "assets/"):
        """
        Inicializa el chatbot con Agno.

        Args:
            documents_directory: Directorio que contiene los archivos PDF y Excel
        """
        self.documents_directory = documents_directory
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
                model=Claude(id="claude-sonnet-4-5"),
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
        """Carga documentos PDF y Excel usando PDFReader de Agno y pandas."""
        try:
            if not os.path.exists(self.documents_directory):
                logger.warning(f"Directorio {self.documents_directory} no existe")
                return

            # Cargar archivos PDF
            pdf_files = list(Path(self.documents_directory).glob("*.pdf"))
            excel_files = list(Path(self.documents_directory).glob("*.xlsx")) + list(
                Path(self.documents_directory).glob("*.xls")
            )

            if not pdf_files and not excel_files:
                logger.warning(
                    f"No se encontraron archivos PDF o Excel en {self.documents_directory}"
                )
                return

            if pdf_files:
                pdf_reader = PDFReader()
                for pdf_file in pdf_files:
                    try:
                        logger.info(f"Cargando PDF: {pdf_file.name}")
                        documents = pdf_reader.read(str(pdf_file))

                        for doc in documents:
                            wrapped_doc = SimpleDocument(
                                content=f"ARCHIVO PDF: {pdf_file.name}\n\n{doc.content}",
                                file_name=pdf_file.name,
                                file_type="PDF",
                            )
                            self.documents.append(wrapped_doc)
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
        """Crea contexto limitado a partir de los documentos."""
        if not self.documents:
            return ""

        context_parts = []
        total_length = 0
        max_context_length = 50000

        for doc in self.documents:
            file_name = getattr(doc, "file_name", "Desconocido")
            file_type = getattr(doc, "file_type", "Desconocido")

            doc_content = f"\n\n=== DOCUMENTO: {file_name} (Tipo: {file_type}) ===\n{doc.content}\n"

            if total_length + len(doc_content) > max_context_length:
                remaining = max_context_length - total_length
                if remaining > 100:
                    doc_content = doc_content[:remaining] + "...\n[DOCUMENTO TRUNCADO]"
                    context_parts.append(doc_content)
                break

            context_parts.append(doc_content)
            total_length += len(doc_content)

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
                response = self.agent.run(question)
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
        if not os.path.exists(self.documents_directory):
            return []

        documents = []
        documents.extend([f.name for f in Path(self.documents_directory).glob("*.pdf")])
        documents.extend(
            [f.name for f in Path(self.documents_directory).glob("*.xlsx")]
        )
        documents.extend([f.name for f in Path(self.documents_directory).glob("*.xls")])

        return documents

    def get_agent_info(self) -> Dict[str, Any]:
        """Obtiene información sobre el estado del agent."""
        return {
            "ready": self.is_ready(),
            "documents_directory": self.documents_directory,
            "available_documents": self.get_available_documents(),
            "model": "Claude Sonnet 4.5 (via Agno)",
            "documents_loaded": len(self.documents),
            "framework": "Agno",
            "supports_pdf": True,
            "supports_excel": True,
            "uses_semantic_search": False,
        }


# Instancia global
agno_chatbot = AgnoDocumentChatbot()


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