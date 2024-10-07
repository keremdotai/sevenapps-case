import http
import logging
import os
from copy import copy
from datetime import datetime, timedelta

import click
from uvicorn.logging import AccessFormatter as UvicornAccessFormatter

# Constants
TRACE_LOG_LEVEL = 5
PID_MAX_LENGTH = len(str(os.getpid())) if len(str(os.getpid())) > 3 else 3 + 5
LOCAL_OFFSET = timedelta(hours=3)


class AccessFormatter(UvicornAccessFormatter):
    """
    Formatter for access handler.
    This formatter colorizes the status code \
    and the other HTTP related information.

    Attributes
    ----------
    level_name_colors : dict
        A dictionary that maps log levels to color functions.
    """

    level_name_colors = {
        TRACE_LOG_LEVEL: lambda level_name: click.style(str(level_name), fg="blue", bold=True),
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan", bold=True),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green", bold=True),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow", bold=True),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red", bold=True),
        logging.CRITICAL: lambda level_name: click.style(str(level_name), fg="bright_red", bold=True),
    }

    def color_default(self, asctime: str, level_no: int) -> str:
        """
        Colorize the asctime based on the log level.

        Parameters
        ----------
        asctime : str | datetime
            The asctime to colorize.

        level_no : int
            The log level number.

        Returns
        -------
        colored_asctime : str
            The colorized asctime.
        """

        def default(asctime: str) -> str:
            return str(asctime)

        func = self.level_name_colors.get(level_no, default)

        return func(asctime)

    def get_status_code(self, status_code: int) -> str:
        """
        Get the status code and its phrase.
        If no valid status code is provided, \
        the status code is retured without a phrase.
        If use_colors is True, the status code is colorized.

        Parameters
        ----------
        status_code : int
            The status code.

        Returns
        -------
        status_and_phrase : str
            The status code and its phrase.
        """
        try:
            status_phrase = http.HTTPStatus(status_code).phrase
        except ValueError:
            if status_code == 499:
                status_phrase = "Client Closed Request"
            else:
                status_phrase = ""
        status_and_phrase = "%s %s" % (status_code, status_phrase)

        if self.use_colors:

            def default(code: int) -> str:
                return status_and_phrase

            func = self.status_code_colours.get(status_code // 100, default)
            return func(status_and_phrase)

        return status_and_phrase

    def normalize_default(self, recordcopy: logging.LogRecord) -> logging.LogRecord:
        """
        Formats the default log record's message such that \
        the record's attributes are changed with a pattern \
        and the message is colorized.

        Parameters
        ----------
        recordcopy : logging.LogRecord
            The log record to format.
        """
        correlation_id = recordcopy.__dict__.get("correlation_id", "")
        levelname = recordcopy.levelname
        asctime = recordcopy.__dict__.get("asctime", "")
        if asctime != "":
            asctime = (datetime.strptime(asctime, "%Y-%m-%d %H:%M:%S,%f") + LOCAL_OFFSET).strftime(
                "%Y-%m-%d %H:%M:%S,%f"
            )[:-3]
        _norm_process = "PID: " + str(recordcopy.__dict__.get("process", ""))
        process = _norm_process + " " * (PID_MAX_LENGTH - len(_norm_process))
        message = recordcopy.__dict__.get("message", "")
        module = recordcopy.__dict__.get("module", "")
        lineno = recordcopy.__dict__.get("lineno", "")
        seperator = " " * (8 - len(recordcopy.levelname))

        # Colorize if use_colors is True
        if self.use_colors:
            correlation_id = self.color_default(correlation_id, recordcopy.levelno)
            levelname = self.color_level_name(levelname, recordcopy.levelno)
            asctime = self.color_default(asctime, recordcopy.levelno)
            message = click.style(message, fg="bright_white")
            process = self.color_default(process, recordcopy.levelno)
            module = click.style(str(module), fg="bright_white")
            lineno = click.style(str(lineno), fg="bright_white")

        # Update the record's attributes
        recordcopy.asctime = asctime
        recordcopy.message = message
        recordcopy.module = module
        recordcopy.lineno = lineno
        recordcopy.__dict__["pid"] = process
        recordcopy.__dict__["correlation_id"] = correlation_id
        recordcopy.__dict__["levelprefix"] = levelname + ":" + seperator

    def formatMessage(self, record: logging.LogRecord) -> str:
        """
        Format the HTTP log record's message such that \
        the default log record is formatted and \
        the HTTP message is created.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        formatted_message : str
            The formatted message.
        """
        recordcopy = copy(record)
        self.normalize_default(recordcopy)
        client_addr, method, full_path, http_version, status_code = recordcopy.args
        status_code = self.get_status_code(int(status_code))
        request_line = "%s %s HTTP/%s" % (method, full_path, http_version)
        if self.use_colors:
            request_line = click.style(request_line, bold=True)
        recordcopy.message = f'{client_addr} - "{request_line}" {status_code}'

        return super().formatMessage(recordcopy)
