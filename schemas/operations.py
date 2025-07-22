from pydantic import BaseModel, Field

class Pow(BaseModel):
    base: int = Field(..., ge=0, description="Base integer")
    exponent: int = Field(..., ge=0, description="Exponent (≥ 0)")
    result: int | None = Field(
        None,
        description="Computed value. Populated only in responses."
    )

class Fibonacci(BaseModel):
    n: int = Field(..., ge=0, description="Index n (≥ 0)")
    result: int | None = Field(None, description="Fₙ (calculated by server)")

class Factorial(BaseModel):
    n: int = Field(..., ge=0, description="Non-negative integer")
    result: int | None = Field(None, description="n! (calculated by server)")