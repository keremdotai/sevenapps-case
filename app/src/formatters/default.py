import logging
import os
from copy import copy
from datetime import datetime, timedelta

import click
from uvicorn.logging import DefaultFormatter as UvicornDefaultFormatter

# Constants
TRACE_LOG_LEVEL = 5
PID_MAX_LENGTH = len(str(os.getpid())) if len(str(os.getpid())) > 3 else 3 + 5
LOCAL_OFFSET = timedelta(hours=3)


# Formatters
class DefaultFormatter(UvicornDefaultFormatter):
    """
    Formatter for default handler.
    This formatter colorizes the log level name and the message.

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

    def color_default(self, asctime: str | datetime, level_no: int) -> str:
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

        def default(asctime: str | datetime) -> str:
            return str(asctime)

        func = self.level_name_colors.get(level_no, default)

        return func(asctime)

    def formatMessage(self, record: logging.LogRecord) -> str:
        """
        Formats the log record's message such that \
        the record's attributes are changed with a pattern \
        and the message is colorized.

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
            if "color_message" in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__["color_message"]
                recordcopy.__dict__["message"] = recordcopy.getMessage()

        # Update the record's attributes
        recordcopy.asctime = asctime
        recordcopy.message = message
        recordcopy.module = module
        recordcopy.lineno = lineno
        recordcopy.__dict__["correlation_id"] = correlation_id
        recordcopy.__dict__["pid"] = process
        recordcopy.__dict__["levelprefix"] = levelname + ":" + seperator

        return super().formatMessage(recordcopy)
