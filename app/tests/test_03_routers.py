assert __name__ == "__main__", "This script is not meant to be imported."

import subprocess
import unittest
from pathlib import Path

from utils import JSONTestRunner, add_path

add_path()


class TestRouters(unittest.TestCase):
    """
    Test the routers.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the class for the tests.
        """
        cls.path = str(Path(__file__).parents[2])

        subprocess.run(
            ["docker", "compose", "-f", f"{cls.path}/docker-compose.yml", "up", "-d", "mongodb", "redis"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        from src.main import app
        from fastapi.testclient import TestClient

        cls.app = app
        cls.client = TestClient

        # Define placeholders
        cls.pdf_id = None

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Tear down the class after the tests.
        """
        subprocess.run(
            ["docker", "compose", "-f", f"{cls.path}/docker-compose.yml", "down"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def test_00_upload_pdf_with_valid_pdf(self) -> None:
        """
        Test the upload of a PDF document with a valid PDF file.

        `GET /v1/pdf`
        """
        with self.client(self.app) as client:
            response = client.post(
                "/v1/pdf",
                files={"file": ("case-000.pdf", open(Path(__file__).parent / "data" / "case-000.pdf", "rb"))},
            )
            self.assertEqual(response.status_code, 201)

        data = response.json()
        pdf_id = data["pdf_id"]
        TestRouters.pdf_id = pdf_id

    def test_01_upload_pdf_with_no_text_pdf(self) -> None:
        """
        Test the upload of a PDF document with a no-text PDF file.

        `GET /v1/pdf`
        """
        with self.client(self.app) as client:
            response = client.post(
                "/v1/pdf",
                files={"file": ("case-001.pdf", open(Path(__file__).parent / "data" / "case-001.pdf", "rb"))},
            )
            self.assertEqual(response.status_code, 500)

    def test_02_upload_pdf_with_invalid_format(self) -> None:
        """
        Test the upload of a PDF document with an invalid file format.

        `GET /v1/pdf`
        """
        with self.client(self.app) as client:
            response = client.post(
                "/v1/pdf",
                files={
                    "file": ("case-002.txt", open(Path(__file__).parent / "data" / "case-003.jpeg", "rb"))
                },
            )
            self.assertEqual(response.status_code, 400)

    def test_03_chat_correctly(self) -> None:
        """
        Test the chat with a correct message and existing pdf id.

        `POST /v1/chat/{pdf_id}`
        """
        with self.client(self.app) as client:
            response = client.post(
                f"/v1/chat/{TestRouters.pdf_id}",
                json={"message": "What is the title of this paper?"},
            )
            self.assertEqual(response.status_code, 200)

    def test_04_chat_incorrect_pdf_id(self) -> None:
        """
        Test the chat with an incorrect pdf id.

        `POST /v1/chat/{pdf_id}`
        """
        with self.client(self.app) as client:
            response = client.post(
                f"/v1/chat/{TestRouters.pdf_id[:-5] + '12345'}",
                json={"message": "What is the title of this paper?"},
            )
            self.assertEqual(response.status_code, 404)

    def test_05_chat_incorrect_request_body(self) -> None:
        """
        Test the chat with an incorrect request body.

        `POST /v1/chat/{pdf_id}`
        """
        with self.client(self.app) as client:
            response = client.post(
                f"/v1/chat/{TestRouters.pdf_id}",
                json={"text": "What is the title of this paper?"},
            )
            self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRouters)
    runner = JSONTestRunner()
    runner.run(suite, "routers")
