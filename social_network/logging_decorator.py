"""
Logging Decorator for Flow Tracing
----------------------------------

This module defines a lightweight logging decorator for tracing the flow of
function calls across the application. It helps developers visualize the
sequence of operations and arguments passed, particularly during debugging
and development.

Use this to decorate any function where understanding the call sequence
is important, especially in layers like:
- `menu.py` (UI flow)
- `main.py` (application logic)
- `domain_logic_layer.py` and `data_access_layer.py` (core logic)

Log Level Used: DEBUG

Example Log Output:
    FLOW TRACKING: Executing add_user || args = ({'user_id': 'user01', ...},) || kwargs = {}

Note: This decorator does **not** log return values or exceptions. It's meant
for entry-level tracing only.
"""

from functools import wraps
from loguru import logger


def log_decorator(func):
    """
    Decorator that logs the function name and arguments at DEBUG level when the function is called.

    :param func: Function to be wrapped
    :return: Wrapped function with logging
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(
            "FLOW TRACKING: Executing {} || args = {} || kwargs = {}",
            func.__name__,
            args,
            kwargs,
        )
        return func(*args, **kwargs)

    return wrapper
