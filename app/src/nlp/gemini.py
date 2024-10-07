import os

import google.generativeai as genai

# Environment variable/s
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", None)

if GEMINI_API_KEY is None or GEMINI_MODEL_NAME is None:
    raise Exception("Environment variables for Gemini API are not set properly.")


class ChatClient:
    """
    This client is responsible for interacting with the Gemini API.
    """

    def __init__(self) -> None:
        """
        Constructor method for `ChatClient`.
        """
        genai.configure(api_key=GEMINI_API_KEY)

        self.model_name = GEMINI_MODEL_NAME
        self.system_instructions = """You are an assistant that answers questions solely based on the PDF document content that will be provided to you.
The PDF document will be parsed via Python and its text and its metadata will be extracted.
The text and metadata will be provided to you in the chat.
Any unrelated questions should be responded to with 'I can only answer questions related to the document.'.
Please keep the conversation professional and respectful.
Additionally, please only provide text-based responses.

"""

    def chat(self, metadata: dict, content: str, history: list[dict] | None = None) -> genai.ChatSession:
        """
        Start a chat session with the Gemini API.

        Parameters
        ----------
        metadata : dict
            The metadata of the PDF document.

        content : str
            The text content of the PDF document.

        history : dict | None
            The chat history.

        Returns
        -------
        chat : genai.ChatSession
            The chat session.
        """
        # Create the system instructions
        instructions = (
            self.system_instructions
            + f"""The text content of the PDF document is as follows:
{content}

The metadata of the PDF document is as follows:
{metadata}"""
        )

        # Initialize the model for the chat
        model = genai.GenerativeModel(model_name=self.model_name, system_instruction=instructions)

        # Start the chat
        chat = model.start_chat(history=history)

        return chat
