assert __name__ == "__main__", "This script is not meant to be imported."

import unittest
from pathlib import Path

from utils import JSONTestRunner, add_path

add_path()


class TestNLP(unittest.TestCase):
    """
    Test Natural Language Processing tools.
    """

    def test_00_chat_client(self) -> None:
        """
        Test `nlp.ChatClient` class.
        """
        from src.nlp import ChatClient
        from src.utils import read_pdf_from_bytes

        with open(Path(__file__).parent / "data" / "case-002.pdf", "rb") as file:
            metadata, text = read_pdf_from_bytes("case-002.pdf", file.read())

        client = ChatClient()
        chat = client.chat(metadata, text, None)

        # Check if the chat session is created
        self.assertIsNotNone(chat)

        # Ask a question
        question = """Give us the name of whose resume is this?
This is a unittest. So, please return only the name without punctuation,
special characters (only use alphanumeric characters), whitespaces, and in lowercase."""
        response = chat.send_message(question)

        self.assertEqual(response.text, "kerem avci \n")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNLP)
    runner = JSONTestRunner()
    runner.run(suite, "nlp")
