from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.requests import ClientDisconnect
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget

from ..database import MongoClient
from ..utils import CustomHTTPException, MaxBodySizeError, MaxBodySizeValidator, read_pdf_from_bytes

# Define router
router = APIRouter()


@router.post("/v1/pdf")
async def upload_pdf(request: Request) -> JSONResponse:
    """
    This endpoint is used to upload a PDF file to the server.

    Parameters
    ----------
    request : Request
        Incoming request object containing the PDF file.

    Returns
    -------
    response : JSONResponse
        JSON response containing the status of the request.
    """
    app: FastAPI = request.app
    db: MongoClient = app.state.mongo_client

    # Read the incoming stream
    try:
        # Create a target for the file
        validator = MaxBodySizeValidator()
        file = ValueTarget()
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register("file", file)

        # Read the incoming stream
        async for chunk in request.stream():
            validator.chunk(chunk)
            parser.data_received(chunk)
    # Handle client disconnect
    except ClientDisconnect as e:
        raise CustomHTTPException(
            exception=e,
            status_code=499,
            detail="Client disconnected",
        )
    # Handle file size error
    except MaxBodySizeError as e:
        raise CustomHTTPException(
            exception=e,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Request body size exceeded {validator.max_size} bytes ({e.body_len} bytes received)",
        )
    # Handle other errors
    except Exception as e:
        raise CustomHTTPException(
            exception=e,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file data",
        )

    # Get the filename
    filename = file.multipart_filename

    # Parse the PDF file
    try:
        metadata, text = read_pdf_from_bytes(filename, file.value)
    except Exception as e:
        raise CustomHTTPException(
            exception=e,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse PDF file, please check the file content/format",
        )

    # Insert the PDF document into the database
    try:
        pdf_id = await db.insert_pdf(metadata, text)
    except:
        raise CustomHTTPException(
            exception=e,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert PDF document into the database",
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"pdf_id": pdf_id},
    )
