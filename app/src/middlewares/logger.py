import json
from datetime import datetime
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..database import MongoClient
from ..logger import LOGGER
from ..utils import CustomHTTPException


async def log_to_database(db: MongoClient, log: dict) -> None:
    """
    Log a request with its details to the database.
    If the logging fails, it logs an error message with the log content.

    Parameters
    ----------
    db : MongoClient
        The MongoDB client.

    log : dict
        The log dictionary.
    """
    try:
        await db.insert_log(log)
    except:
        LOGGER.error(f"FAIL TO LOG : {json.dumps(log)}")


class LoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and any possible exception.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        """
        Dispatch method of the middleware.
        It logs the incoming request with its scope and host information.
        Moreover, it logs any possible exception that occurs during the request.

        Parameters
        ----------
        request : Request
            The incoming request object.

        call_next : Callable
            The next callable function in the middleware chain.

        Returns
        -------
        response : Response
            The response object.
        """
        app = request.app
        db: MongoClient = app.state.mongo_client

        # Parse the request's details
        host, port = request.client.host, request.client.port
        scope = request.scope
        http_type, http_version = scope["type"], scope["http_version"]
        method, path = scope["method"], scope["path"]
        request_log = {
            "client": f"{host}:{port}",
            "http": f"{http_type}/{http_version}",
            "path": path,
            "method": method,
        }

        # Log the incoming request to the database
        log = request_log | {
            "level": "info",
            "detail": "Incoming request.",
            "timestamp": datetime.now(),
        }
        await log_to_database(db, log)

        # Run the request
        try:
            response: Response = await call_next(request)

            # Log the response to the database
            log = request_log | {
                "level": "info",
                "detail": "Endpoint returns successfully.",
                "status_code": response.status_code,
                "timestamp": datetime.now(),
            }
            await log_to_database(db, log)

            return response
        # Catch the HTTP exception
        except CustomHTTPException as e:
            # Log the exception to the database
            log = request_log | {
                "level": "error",
                "status_code": e.status_code,
                "detail": e.detail,
                "traceback": e.trace,
                "timestamp": datetime.now(),
            }
            await log_to_database(db, log)

            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
            )
        # Catch any other exception
        except Exception as e:
            # Log the exception to the database
            e = CustomHTTPException(e, status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred.")
            log = request_log | {
                "level": "error",
                "status_code": e.status_code,
                "detail": e.detail,
                "traceback": e.trace,
                "timestamp": datetime.now(),
            }
            await log_to_database(db, log)

            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
            )
