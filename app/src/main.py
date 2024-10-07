from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from . import routers, middlewares
from .database import MongoClient, RedisClient
from .logger import LOGGER
from .nlp import ChatClient


# Lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifespan function for each worker of the FastAPI application.

    Parameters
    ----------
    app : FastAPI
        FastAPI application instance.
    """
    # Create a MongoDB client and check the connection
    mongo_client = MongoClient()
    redis_client = RedisClient()
    chat_client = ChatClient()

    try:
        await mongo_client.ping()
        await redis_client.ping()
    except:
        LOGGER.error("Failed to connect to MongoDB or Redis.")
        exit(1)

    # Set the MongoDB client in the application state
    app.state.mongo_client = mongo_client
    app.state.redis_client = redis_client
    app.state.chat_client = chat_client

    LOGGER.info("The worker is starting...")

    yield

    LOGGER.info("The worker is stopping...")

    # Close the MongoDB client
    await mongo_client.close()
    await redis_client.close()


# FastAPI application instance
app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(routers.chat.router)
app.include_router(routers.pdf.router)

# Middlewares
app.add_middleware(
    middlewares.CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

app.add_middleware(middlewares.LoggerMiddleware)
