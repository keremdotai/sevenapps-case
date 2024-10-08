import os
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorClient

# from pymongo.server_api import ServerApi

# Environment variable/s
MONGODB_HOST = os.getenv("MONGODB_HOST", None)
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", None)
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", None)

if MONGODB_HOST is None or MONGODB_USERNAME is None or MONGODB_PASSWORD is None:
    raise ValueError("MongoDB environment variables are not set.")

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"


class MongoClient:
    """
    MongoDB client class.
    This class provides CRUD operations for the MongoDB database.
    """

    def __init__(self) -> None:
        """
        Constructor method for `MongoClient`.

        Attributes
        ----------
        client : AsyncIOMotorClient
            The MongoDB client.

        db : AsyncIOMotorDatabase
            The database.

        pdfs : AsyncIOMotorCollection
            The collection for PDFs.

        logs : AsyncIOMotorCollection
            The collection for logs.
        """
        self.client = AsyncIOMotorClient(
            host=MONGODB_HOST if not DEV_MODE else "localhost",
            port=27017 if not DEV_MODE else int(os.getenv("MONGODB_PORT", 27017)),
            username=MONGODB_USERNAME,
            password=MONGODB_PASSWORD,
        )

        # Database
        self.db = self.client["sevenapss-case"]

        # Collections
        self.pdfs = self.db["pdfs"]
        self.logs = self.db["logs"]

    async def close(self) -> None:
        """
        Close the MongoDB client.
        """
        self.client.close()

    async def ping(self) -> None:
        """
        Ping the MongoDB client.
        """
        await self.client.admin.command("ping")

    async def insert_pdf(self, metadata: dict, text: str) -> str:
        """
        Insert a PDF document into the database.

        Parameters
        ----------
        metadata : dict
            The metadata of the PDF document.

        text : str
            The text content of the PDF document.

        Returns
        -------
        pdf_id : str
            The ID of the inserted PDF document.
            If the document was not inserted, raise an exception.
        """
        # Insert the PDF document
        result = await self.pdfs.insert_one({"metadata": metadata, "text": text})

        # Check if the document was inserted
        pdf_id = result.inserted_id
        if pdf_id is None:
            raise Exception("Failed to insert pdf document (MongoDB).")

        return str(pdf_id)

    async def find_pdf(self, pdf_id: str | ObjectId) -> dict:
        """
        Find a PDF document by its ID.

        Parameters
        ----------
        pdf_id : str
            The ID of the PDF document.

        Returns
        -------
        pdf : dict
            The PDF document.
            If the PDF document is not found, raise an exception.
        """
        # Find the PDF document
        pdf = await self.pdfs.find_one({"_id": ObjectId(pdf_id)})

        # Check if the document was found
        if pdf is None:
            raise Exception(f"Failed to find document with ID {pdf_id} (MongoDB).")

        return pdf

    async def insert_log(self, log: dict) -> str:
        """
        Insert a log into the database.

        Parameters
        ----------
        log : dict
            The log.

        Returns
        -------
        log_id : str
            The ID of the inserted log.
            If the log was not inserted, raise an exception.
        """
        # Insert the log
        result = await self.logs.insert_one(log)

        # Check if the log was inserted
        log_id = result.inserted_id
        if log_id is None:
            raise Exception("Failed to insert log document (MongoDB).")

        return str(log_id)
