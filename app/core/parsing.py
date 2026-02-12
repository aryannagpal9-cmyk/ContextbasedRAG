from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from pathlib import Path

class DocumentParser:
    def __init__(self):
        # Use simple initialization without custom PdfPipelineOptions
        self.converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF, InputFormat.DOCX, InputFormat.HTML]
        )

    def parse(self, file_path: str):
        """
        Parses a document and returns the Docling document object.
        """
        from app.core.logging_config import logger
        logger.info(f"Initiating Docling parse for: {file_path}")
        try:
            result = self.converter.convert(Path(file_path))
            logger.info(f"Successfully parsed document {file_path}")
            return result.document
        except Exception as e:
            logger.error(f"Docling parse failed for {file_path}: {e}", exc_info=True)
            raise RuntimeError(f"Error parsing document: {e}")
