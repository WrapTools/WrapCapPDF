# WrapCapPDF/pdf_extractor.py

import io
import os
import re
import pymupdf
from pymupdf4llm import to_markdown
import logging

# Logger Configuration
logger = logging.getLogger(__name__)

class CapPDFHandler:
    def __init__(self, resource_path):  # , log_level=logging.INFO
        """Initialize with the PDF path and log level."""
        if not os.path.exists(resource_path):
            raise FileNotFoundError(f"File not found: {resource_path}")

        self.pdf_path = resource_path
        self.memory_file = None

    # Exxtract methods
    def extract_markdown_content(self, cleaned=False, start=None, end=None):
        """Extract Markdown text from all pages, with optional cleaning and text range selection."""
        try:
            # Convert to markdown
            markdown_content = to_markdown(self.pdf_path, write_images=False)

            if cleaned:
                markdown_content = self._remove_images_from_markdown_content(markdown_content)

            # Enhance Markdown formatting
            markdown_content = self._format_markdown_content(markdown_content)

            # Filter content between specified start and end markers if needed
            if start or end:
                start_idx = markdown_content.find(start) if start else 0
                end_idx = markdown_content.find(end, start_idx) if end else len(markdown_content)

                if start_idx == -1 or (end and end_idx == -1):
                    logger.warning("Specified start or end markers not found. Returning full content.")
                    return markdown_content.strip()  # Return full content instead of an error message

                markdown_content = markdown_content[start_idx:end_idx].strip()

            return markdown_content
        except Exception as e:
            logger.error(f"An error occurred while extracting content: {e}")
            return f"An error occurred while extracting content: {e}"

    def extract_text_content(self, start=None, end=None):
        """Extracts plain text from the PDF while preserving paragraph structure but without Markdown formatting."""
        try:
            # Open the PDF and extract text
            with pymupdf.open(self.pdf_path) as doc:
                text_content = "\n\n".join(page.get_text("text") for page in doc)

            # Filter content between specified start and end markers if needed
            if start or end:
                start_idx = text_content.find(start) if start else 0
                end_idx = text_content.find(end, start_idx) if end else len(text_content)

                if start_idx == -1 or (end and end_idx == -1):
                    logger.warning("Specified start or end markers not found. Returning full content.")
                    return text_content.strip()

                text_content = text_content[start_idx:end_idx].strip()

            return text_content
        except Exception as e:
            logger.error(f"An error occurred while extracting text content: {e}")
            return False

    # Helper methods
    @staticmethod
    def _remove_images_from_markdown_content(markdown_content):
        """Remove image tags from Markdown content."""
        return re.sub(r"!\[.*?\]\(.*?\)", "", markdown_content)

    @staticmethod
    def _format_markdown_content(markdown_content):
        """Enhance Markdown formatting by preserving styles and detecting headings."""
        markdown_content = re.sub(r"\*\*(.*?)\*\*", r"**\1**", markdown_content)  # Keep bold
        markdown_content = re.sub(r"__(.*?)__", r"__\1__", markdown_content)  # Keep underline
        markdown_content = re.sub(r"\*(.*?)\*", r"*\1*", markdown_content)  # Keep italic

        # Refined heading detection
        lines = markdown_content.split("\n")
        for i in range(len(lines)):
            if re.match(r'^\s*\*\*[^*]+\*\*\s*$', lines[i]):  # **Bold** on a single line
                lines[i] = f"## {lines[i].strip(' *')}"  # Convert to Heading 2

        return "\n".join(lines)

    def create_output_directory(self, destination):
        """Create the output directory for saving files."""
        output_dir = destination / self.pdf_path.stem
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    # Get methods
    def get_memory_file(self):
        """Load the PDF into memory for reuse."""
        if self.memory_file is None:
            with open(self.pdf_path, "rb") as file:
                self.memory_file = io.BytesIO(file.read())
        self.memory_file.seek(0)  # Ensure reading starts from the beginning
        return self.memory_file

    def get_pdf_title(self):
        """Returns the PDF's title if available, else None."""
        try:
            with pymupdf.open(self.pdf_path) as doc:
                title = doc.metadata.get("title")
                logger.info(f"PDF Title: {title}")
                return title or None
        except Exception as e:
            logger.error(f"An error occurred while retrieving the page title: {e}")
            return None

    def _get_pdf_generation_options(self):
        pass # Future implementation


    # Save methods
    def save_markdown_to_file(self, output_path: str, markdown_content=None, cleaned=False, start=None, end=None):
        """
        Saves extracted Markdown content to a file.
        If markdown_content is provided, it saves that content directly.
        Otherwise, it extracts content first.
        """
        try:
            if markdown_content is None:
                markdown_content = self.extract_markdown_content(cleaned=cleaned, start=start, end=end)

            with open(output_path, "w", encoding="utf-8") as md_file:
                md_file.write(markdown_content)

            logger.info(f"Markdown file saved successfully: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save Markdown file: {e}")

    def save_text_to_file(self, output_path: str, text_content=None, start=None, end=None):
        """
        Saves extracted plain text content to a file.
        If text_content is provided, it saves that content directly.
        Otherwise, it extracts content first.

        :param output_path: The path to save the text file.
        :param text_content: Pre-extracted plain text (optional).
        :param start: Optional start marker for filtering text.
        :param end: Optional end marker for filtering text.
        """
        try:
            if text_content is None:
                text_content = self.extract_text_content(start=start, end=end)

            with open(output_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(text_content)

            logger.info(f"Plain text file saved successfully: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save plain text file: {e}")

    def save_content(self, content, output_path):
        """Save content to a file."""
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.info(f"File saved to: {output_path}")

    # Validation methods
    @staticmethod
    def validate_paths(source, destination):
        """Validate the source file and destination directory for PDF conversion."""
        # Validate the source file
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"The source file {source} does not exist.")
        if source.suffix.lower() != '.pdf':
            raise ValueError("The source file must be a PDF.")

        # Validate the destination directory
        if not destination.exists():
            raise NotADirectoryError(f"The destination directory {destination} does not exist.")
        if not destination.is_dir():
            raise NotADirectoryError(f"The destination path {destination} is not a directory.")
