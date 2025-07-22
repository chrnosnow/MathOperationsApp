"""
Domain-level exception hierarchy.

Convert these to HTTP errors in the API layer.
"""

class MathServiceError(Exception):
    """Base class for math-service exceptions."""


class InvalidInputError(MathServiceError, ValueError):
    """Raised when the caller supplies an invalid argument."""


class OverflowError(MathServiceError):
    """Raised when the result would overflow practical limits."""
