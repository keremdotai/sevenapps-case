assert __name__ == "__main__", "This script is not meant to be imported."

import unittest
from pathlib import Path

from utils import JSONTestRunner, add_path

add_path()


class TestUtilities(unittest.TestCase):
    """
    Test the utilities.
    """

    def test_00_detect_language(self) -> None:
        """
        Test `utils.detect_language` function.
        """
        from src.utils.text import detect_language

        # Test with English text
        text = "Hello, world!"
        self.assertEqual(detect_language(text), "en")

        # Test with Turkish text
        text = "Merhaba, dünya!"
        self.assertEqual(detect_language(text), "tr")

    def test_01_clean_text(self) -> None:
        """
        Test `utils.clean_text` function.
        """
        from src.utils.text import clean_text

        text = "Hello, world!\n\n    This para-\ngraph contains non-ASCII characters: öçşğüı\n"
        cleaned_text = "Hello, world! This paragraph contains non-ASCII characters:"

        self.assertEqual(clean_text(text), cleaned_text)

    def test_02_read_pdf_from_bytes_with_proper_pdf(self) -> None:
        """
        Test `utils.read_pdf_from_bytes` function with a proper PDF file.
        """
        from src.utils import read_pdf_from_bytes

        with open(Path(__file__).parent / "data" / "case-000.pdf", "rb") as file:
            _, pdf = read_pdf_from_bytes("case-000.pdf", file.read())

        self.assertGreater(len(pdf), 0)

    def test_03_read_pdf_from_bytes_with_empty_pdf(self) -> None:
        """
        Test `utils.read_pdf_from_bytes` function with an empty PDF file.
        """
        from src.utils import read_pdf_from_bytes

        try:
            with open(Path(__file__).parent / "data" / "case-001.pdf", "rb") as file:
                read_pdf_from_bytes("case-000.pdf", file.read())
            raise Exception("Failed to raise an exception for an empty PDF file.")
        except Exception as e:
            self.assertEqual(str(e), "Empty PDF file or unsupported format")

    def test_04_read_pdf_from_bytes_with_unsupported_format(self) -> None:
        """
        Test `utils.read_pdf_from_bytes` function with an unsupported format.
        """
        from src.utils import read_pdf_from_bytes

        try:
            with open(Path(__file__).parent / "data" / "case-003.jpeg", "rb") as file:
                read_pdf_from_bytes("case-000.pdf", file.read())
            raise Exception("Failed to raise an exception for an unsupported format.")
        except Exception as e:
            self.assertEqual(str(e), "Empty PDF file or unsupported format")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUtilities)
    runner = JSONTestRunner()
    runner.run(suite, "utils")
