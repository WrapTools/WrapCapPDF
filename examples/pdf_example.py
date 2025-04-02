# pdf_example.py

# Configure Logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format = '%(name)s - %(levelname)s - %(message)s (line: %(lineno)d)',
    handlers=[
        logging.StreamHandler(),  # Log to console
        # logging.FileHandler('app.log')  # Log to file
    ]
)

from WrapCapPDF.pdf_extractor import CapPDFHandler
from pathlib import Path

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    pdf_path = input("Enter a full pdf path to extract:")
    pdf_directory = Path(pdf_path).parent
    file_stem = Path(pdf_path).stem  # '2025-02194' (removes '.pdf')
    new_directory = Path(pdf_directory) / file_stem  # Create a new directory named after the file stem

    # Ensure the new directory exists
    logger.info(f"Creating directory: {new_directory}")
    new_directory.mkdir(parents=True, exist_ok=True)

    # Define the paths for the new files inside the directory
    md_output_filename = str(new_directory / f"{file_stem}.md")
    txt_output_filename = str(new_directory / f"{file_stem}.txt")
    new_pdf_path = new_directory / Path(pdf_path).name

    handler = CapPDFHandler(pdf_path)

    # Get PDF Title
    logger.info(f"Extracting PDF title from: {pdf_path}")
    pdf_title = handler.get_pdf_title() or "Untitled"

    # Extract content
    markdown_text = handler.extract_markdown_content(cleaned=True)
    plain_text = handler.extract_text_content()

    # Save Markdown
    handler.save_markdown_to_file(md_output_filename, markdown_content=markdown_text)

    # Save Plain Text
    handler.save_text_to_file(txt_output_filename, text_content=plain_text)

    # Move the original PDF to the new directory
    Path(pdf_path).rename(new_pdf_path)

    # Print extracted Markdown & metadata
    print(f"PDF Title: {pdf_title}")
    print(f"Markdown saved as: {md_output_filename}")
    print(f"Plain text saved as: {txt_output_filename}")
    print(f"PDF moved to: {new_pdf_path}")