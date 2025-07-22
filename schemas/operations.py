"""
Request / response models for math operations.

Works with Pydantic v2 (FastAPI ≥ 0.110).
"""

from typing import Annotated

from pydantic import BaseModel, Field, RootModel, conint, confloat


# --------------------------------------------------------------------------- #
# Shared helpers                                                              #
# --------------------------------------------------------------------------- #
# Strict numeric types to avoid implicit coercion (e.g., "3" ➜ int 3).
StrictFloat = Annotated[float, confloat(strict=True)]
StrictInt = Annotated[int, conint(strict=True)]


# --------------------------------------------------------------------------- #
# Pow                                                                         #
# --------------------------------------------------------------------------- #
class PowRequest(BaseModel):
    base: StrictFloat = Field(..., description="Base number", examples=[2])
    exponent: StrictFloat = Field(..., description="Exponent", examples=[8])

    model_config = {"json_schema_extra": {"examples": [{"base": 2, "exponent": 8}]}}


class PowResponse(BaseModel):
    result: float = Field(..., description="base ** exponent")


# --------------------------------------------------------------------------- #
# Fibonacci                                                                   #
# --------------------------------------------------------------------------- #
class FibonacciRequest(BaseModel):
    n: StrictInt = Field(
        ...,
        ge=0,
        le=10_000,
        description="0-based index (safety-capped at 10 000)",
        examples=[10],
    )

    model_config = {
        "json_schema_extra": {"examples": [{"n": 10}]},
    }


class FibonacciResponse(BaseModel):
    result: int = Field(..., description="n-th Fibonacci number (0-indexed)")


# --------------------------------------------------------------------------- #
# Factorial                                                                   #
# --------------------------------------------------------------------------- #
class FactorialRequest(BaseModel):
    n: StrictInt = Field(
        ...,
        ge=0,
        le=5_000,
        description="Integer for which to compute n! (≤ 5 000 safeguard)",
        examples=[5],
    )

    model_config = {
        "json_schema_extra": {"examples": [{"n": 5}]},
    }


class FactorialResponse(BaseModel):
    result: int = Field(..., description="n!")


# --------------------------------------------------------------------------- #
# Standard error envelope (optional)                                          #
# --------------------------------------------------------------------------- #
class ErrorResponse(RootModel):
    """Uniform 4xx/5xx error payload used by the API router."""

    root: str = Field(..., examples=["Inputs must be finite numbers."])
