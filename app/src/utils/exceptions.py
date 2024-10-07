import sys
import traceback


class CustomHTTPException(Exception):
    """
    Custom HTTP exception that includes the status code, \
    detail message, and traceback.
    """

    def __init__(self, exception: Exception | None, status_code: int, detail: str) -> None:
        """
        Constructor method for `CustomHTTPException`.

        Parameters
        ----------
        exception : Exception | None
            The exception that occurred.

        status_code : int
            The status code of the exception.

        detail : str
            The detail message of the exception.
        """
        self.trace = self._trace(exception) if exception is not None else None
        self.status_code = status_code
        self.detail = detail

    def _trace(self, exception: Exception) -> dict:
        """
        Get the traceback of an exception as a string.

        Parameters
        ----------
        exception : Exception
            The exception for which to get the traceback.

        Returns
        -------
        trace : dict
            The traceback of the exception.
        """
        ex_repr = repr(exception)
        ex_type, ex_value, ex_traceback = sys.exc_info()
        trace_back = traceback.extract_tb(ex_traceback)

        # Create the trace dictionary
        trace = {}

        # Add the exception type and message
        trace["repr"] = ex_repr
        trace["type"] = ex_type.__name__
        trace["message"] = str(ex_value)

        # Add the details of the traceback
        trace["details"] = []

        for tb in trace_back:
            trace_ = {"file": tb.filename, "function": tb.name, "lineno": tb.lineno, "line": tb.line}
            trace["details"].append(trace_)

        return trace
