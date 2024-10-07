import os

# Environment variable/s
MAX_BODY_SIZE = int(os.getenv("MAX_BODY_SIZE_MB", 1))


class MaxBodySizeError(Exception):
    """
    A special exception for when the body size is too large.
    """

    def __init__(self, body_len: str) -> None:
        """
        Constructor method for `MaxBodySizeError`.

        Parameters
        ----------
        body_len : str
            The length of the body that caused the error.
        """
        self.body_len = body_len


class MaxBodySizeValidator:
    """
    Validator for the maximum body size.
    If the body size exceeds the maximum size, raise a `MaxBodySizeError`.
    """

    def __init__(self):
        """
        Constructor method for `MaxBodySizeValidator`.

        Attributes
        ----------
        body_len : int
            The length of the body.

        max_size : int
            The maximum size of the body.
            It is set to the value of the `MAX_BODY_SIZE_MB` environment variable.
        """
        self.body_len = 0
        self.max_size = MAX_BODY_SIZE * 1024 * 1024

    def chunk(self, chunk: bytes) -> None:
        """
        Increment the body length by the length of the chunk.

        Parameters
        ----------
        chunk : bytes
            The chunk to add to the body length.

        Raises
        ------
        MaxBodySizeError
            If the body length exceeds the maximum size.
        """

        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeError(body_len=self.body_len)
