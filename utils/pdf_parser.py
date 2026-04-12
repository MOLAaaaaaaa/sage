"""PDF parser for geological literature."""

from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF
from loguru import logger


class PDFParser:
    """Parse PDF documents and extract text."""

    def __init__(self):
        """Initialize PDF parser."""
        pass

    def parse_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        try:
            doc = fitz.open(pdf_path)
            text_content = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{text}")

            doc.close()
            full_text = "\n\n".join(text_content)

            logger.info(f"Parsed PDF: {pdf_path.name} ({len(full_text)} characters)")
            return full_text

        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path}: {e}")
            raise

    def parse_pdf_with_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Parse PDF and extract text with metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with text and metadata
        """
        try:
            doc = fitz.open(pdf_path)

            # Extract metadata
            metadata = {
                "title": doc.metadata.get("title", pdf_path.stem),
                "author": doc.metadata.get("author", "Unknown"),
                "subject": doc.metadata.get("subject", ""),
                "pages": len(doc),
                "filename": pdf_path.name,
                "filepath": str(pdf_path),
            }

            # Extract text by pages
            pages = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().strip()
                if text:
                    pages.append({
                        "page_number": page_num + 1,
                        "content": text,
                    })

            doc.close()

            logger.info(f"Parsed PDF with metadata: {pdf_path.name} ({len(pages)} pages)")

            return {
                "metadata": metadata,
                "pages": pages,
                "full_text": "\n\n".join([p["content"] for p in pages]),
            }

        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path}: {e}")
            raise

    def batch_parse(self, pdf_dir: Path) -> List[Dict[str, Any]]:
        """Parse all PDFs in a directory.

        Args:
            pdf_dir: Directory containing PDF files

        Returns:
            List of parsed documents
        """
        pdf_files = list(pdf_dir.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return []

        documents = []
        for pdf_file in pdf_files:
            try:
                doc = self.parse_pdf_with_metadata(pdf_file)
                documents.append(doc)
            except Exception as e:
                logger.error(f"Failed to parse {pdf_file.name}: {e}")

        logger.info(f"Batch parsed {len(documents)}/{len(pdf_files)} PDFs")
        return documents
