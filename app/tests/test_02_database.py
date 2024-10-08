assert __name__ == "__main__", "This script is not meant to be imported."

import asyncio
import secrets
import subprocess
import unittest
from pathlib import Path

from utils import JSONTestRunner, add_path

add_path()


class TestDatabases(unittest.TestCase):
    """
    Test MongoDB and Redis databases.
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

        from src.database import MongoClient, RedisClient

        cls.mongo_client = MongoClient()
        cls.redis_client = RedisClient()
        cls.loop = asyncio.get_event_loop()

        # Define placehorlders
        cls.pdf_id = None
        cls.sample_key = secrets.token_hex(16)

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

    def test_00_ping_mongodb(self) -> None:
        """
        Test the connection to MongoDB.

        `database.mongo.MongoClient.ping()`
        """
        self.loop.run_until_complete(self.mongo_client.ping())

    def test_01_insert_pdf(self) -> None:
        """
        Test the insertion of a PDF document into MongoDB.

        `database.mongo.MongoClient.insert_pdf()`
        """
        sample_metadata = {
            "name": "sample.pdf",
            "size": 1000,
            "content_type": "application/pdf",
        }
        sample_text = "This is a sample PDF document."

        pdf_id = self.loop.run_until_complete(self.mongo_client.insert_pdf(sample_metadata, sample_text))
        TestDatabases.pdf_id = pdf_id

    def test_02_find_pdf_with_existing_pdf(self) -> None:
        """
        Test the retrieval of a PDF document from MongoDB.

        `database.mongo.MongoClient.find_pdf()`
        """
        pdf = self.loop.run_until_complete(self.mongo_client.find_pdf(TestDatabases.pdf_id))
        self.assertIsNotNone(pdf)

    def test_03_find_pdf_with_non_existing_pdf(self) -> None:
        """
        Test the retrieval of a non-existing PDF document from MongoDB.

        `database.mongo.MongoClient.find_pdf()`
        """
        pdf_id = self.pdf_id[:-5] + "12345"
        try:
            self.loop.run_until_complete(self.mongo_client.find_pdf(pdf_id))
            raise Exception("Failed to raise an exception for a non-existing PDF document.")
        except Exception as e:
            self.assertEqual(str(e), f"Failed to find document with ID {pdf_id} (MongoDB).")

    def test_04_close_mongodb(self) -> None:
        """
        Test the closing of the MongoDB client.

        `database.mongo.MongoClient.close()`
        """
        self.loop.run_until_complete(self.mongo_client.close())

    def test_05_ping_redis(self) -> None:
        """
        Test the connection to Redis.

        `database.redis.RedisClient.ping()`
        """
        self.loop.run_until_complete(self.redis_client.ping())

    def test_06_push_item_to_redis(self) -> None:
        """
        Test the pushing of an item to a list in Redis.

        `database.redis.RedisClient.push()`
        """
        sample_content = [
            {"name": "sample1.pdf", "size": 1000},
            {"name": "sample2.pdf", "size": 2000},
            {"name": "sample3.pdf", "size": 3000},
        ]

        self.loop.run_until_complete(self.redis_client.push(self.sample_key, sample_content))

    def test_07_get_length_of_redis_list(self) -> None:
        """
        Test the retrieval of the length of a list in Redis.

        `database.redis.RedisClient.length()`
        """
        length = self.loop.run_until_complete(self.redis_client.length(self.sample_key))
        self.assertEqual(length, 3)

    def test_08_pop_item_from_redis(self) -> None:
        """
        Test the popping of an item from a list in Redis.

        `database.redis.RedisClient.pop()`
        """
        self.loop.run_until_complete(self.redis_client.pop(self.sample_key))

        length = self.loop.run_until_complete(self.redis_client.length(self.sample_key))
        self.assertEqual(length, 2)

    def test_9_get_items_from_redis(self) -> None:
        """
        Test the retrieval of items from a list in Redis.

        `database.redis.RedisClient.get()`
        """
        sample_content = [
            {"name": "sample2.pdf", "size": 2000},
            {"name": "sample3.pdf", "size": 3000},
        ]

        content = self.loop.run_until_complete(self.redis_client.get(self.sample_key))
        self.assertEqual(content, sample_content)

    def test_10_close_redis(self) -> None:
        """
        Test the closing of the Redis client.

        `database.redis.RedisClient.close()`
        """
        self.loop.run_until_complete(self.redis_client.close())


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabases)
    runner = JSONTestRunner()
    runner.run(suite, "database")
