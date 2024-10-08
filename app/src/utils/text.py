import re

from langdetect import DetectorFactory, detect

# Set the seed for the language detector
DetectorFactory.seed = 0


def clean_text(text: str) -> str:
    """
    Clean the text by removing extra spaces, newlines, \
    hyphenated line breaks, and non-ASCII characters.

    Parameters
    ----------
    text : str
        The text to clean.

    Returns
    -------
    cleaned_text : str
        The cleaned text.
    """
    text = re.sub(r"-\n", "", text)  # Remove hyphenated line breaks
    text = re.sub(r"\n+", "\n", text)  # Remove extra newlines
    text = re.sub(r"\s+", " ", text)  # Remove extra spaces
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # Remove non-ASCII characters

    return text.strip()


def detect_language(text: str) -> str:
    """
    Detect the language of the given text.

    Parameters
    ----------
    text : str
        The text to analyze.

    Returns
    -------
    language : str
        The detected language with ISO 639-1 code.
        If the language cannot be detected, return "unknown".
    """
    return detect(text)
