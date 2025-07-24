"""
Domain-level exception hierarchy.

Convert these to HTTP errors in the API layer.
"""


class MathServiceErr(Exception):
    """Base class for math-service exceptions."""


class InvalidInputErr(MathServiceErr, ValueError):
    """Raised when the caller supplies an invalid argument."""


class OverflowErr(MathServiceErr):
    """Raised when the result would overflow practical limits."""
