from functools import wraps
from io import StringIO
from unittest.mock import patch


def silence_ingest_output(test_method):
    """
    Decorator to silence command output in tests.
    """

    @wraps(test_method)
    def wrapper(*args, **kwargs):
        with patch("sys.stdout", new_callable=StringIO):
            return test_method(*args, **kwargs)

    return wrapper
