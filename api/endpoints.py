"""
HTTP routes for math operations.
"""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from deps import get_session
from schemas.operations import (
    PowRequest,
    PowResponse,
    FibonacciRequest,
    FibonacciResponse,
    FactorialRequest,
    FactorialResponse,
)
from services.math_service import (
    calc_pow,
    calc_fibonacci,
    calc_factorial,
)

router = APIRouter(prefix="/api/v1", tags=["math"])


# --------------------------------------------------------------------------- #
# Routes                                                                      #
# --------------------------------------------------------------------------- #
@router.post(
    "/pow",
    response_model=PowResponse,
    responses={400: {"model": PowResponse}},  # placeholder; overridden globally
)
async def pow_endpoint(
    payload: PowRequest,
    session: AsyncSession = Depends(get_session),
) -> PowResponse:
    """Compute `base ** exponent`."""
    result = await calc_pow(
        base=payload.base,
        exponent=payload.exponent,
        session=session,
    )
    return PowResponse(result=result)


@router.post(
    "/fibonacci",
    response_model=FibonacciResponse,
)
async def fibonacci_endpoint(
    payload: FibonacciRequest,
    session: AsyncSession = Depends(get_session),
) -> FibonacciResponse:
    """Return the *n*-th Fibonacci number (0-indexed)."""
    result = await calc_fibonacci(n=payload.n, session=session)
    return FibonacciResponse(result=result)


@router.post(
    "/factorial",
    response_model=FactorialResponse,
)
async def factorial_endpoint(
    payload: FactorialRequest,
    session: AsyncSession = Depends(get_session),
) -> FactorialResponse:
    """Return *n*!."""
    result = await calc_factorial(n=payload.n, session=session)
    return FactorialResponse(result=result)


# --------------------------------------------------------------------------- #
# Misc                                                                        #
# --------------------------------------------------------------------------- #
@router.get("/healthz", tags=["meta"])
async def health_check() -> dict[str, str]:
    """Lightweight liveness probe for Kubernetes / Docker."""
    return {"status": "ok"}
