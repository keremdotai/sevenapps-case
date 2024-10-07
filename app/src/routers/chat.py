from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from ..database import MongoClient, RedisClient
from ..nlp import ChatClient
from ..utils import CustomHTTPException

# Define router
router = APIRouter()


@router.post("/v1/pdf/{pdf_id}")
async def chat_about_pdf(request: Request, pdf_id: str) -> JSONResponse:
    """
    This endpoint is used to chat with the bot using the uploaded PDF file.
    """
    app: FastAPI = request.app
    db: MongoClient = app.state.mongo_client
    cache: RedisClient = app.state.redis_client
    client: ChatClient = app.state.chat_client

    # Get and validate the request body
    try:
        message = ChatRequest(**(await request.json())).message
    except Exception as e:
        raise CustomHTTPException(
            exception=e,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request body",
        )

    # Find the PDF in the database
    try:
        pdf = db.find_pdf(pdf_id)
    except Exception as e:
        raise CustomHTTPException(
            exception=e,
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found",
        )

    # Chat with the bot using the message, text, metadata, and history
    try:
        # Get the chat history from Redis
        history = cache.get(pdf_id)

        # Create chat session
        chat = client.chat(pdf["metadata"], pdf["text"], history)

        # Send the message to the bot
        response = []
        async for part in chat.send_message_async(message, stream=True):
            response.append(part["content"])
        response = "".join(response)

        print(f"Response : {response}")

        # Update the chat history in Redis
        cache.push(
            pdf_id,
            [
                {"role": "user", "parts": message},
                {"role": "model", "parts": response},
            ],
        )
    except Exception as e:
        raise CustomHTTPException(
            exception=e,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to chat with the bot",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"response": response},
    )


# Request body model
class ChatRequest(BaseModel):
    """
    Request body model for the chat endpoint.
    Inputs other than this model's attributes will be ignored.

    Attributes
    ----------
    message : str
        The message to send to the bot.
    """

    model_config = ConfigDict(extra="ignore")

    message: str
