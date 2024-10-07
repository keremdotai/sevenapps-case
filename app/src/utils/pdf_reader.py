from io import BytesIO

import pymupdf

from .text import clean_text, detect_language


def read_pdf_from_bytes(filename: str, pdf_bytes: bytes) -> tuple[dict, str]:
    """
    Read a PDF file from bytes.
    Return the metadata and text content of the PDF file.

    Parameters
    ----------
    filename : str
        The name of the PDF file.

    pdf_bytes : bytes
        The PDF file as bytes.

    Returns
    -------
    metadata : dict
        The metadata of the PDF file.

    text : str
        The text content of the PDF file.
    """
    with pymupdf.Document(stream=BytesIO(pdf_bytes), filetype="pdf") as doc:
        text = ""
        page_counter = 0

        for page in doc:
            page_counter += 1
            # Create a text page from the PDF page
            textpage = page.get_textpage()
            text += textpage.extractText() + "\n"

        metadata = doc.metadata
        metadata = {key: metadata[key] for key in ["title", "author", "subject", "keywords"]}
        metadata["filename"] = filename
        metadata["page_count"] = page_counter

    # Clean the text
    text = clean_text(text)
    if len(text) == 0:
        raise Exception("Empty PDF file or unsupported format")

    # Detect the language of the text
    metadata["language"] = detect_language(text)

    return metadata, text
