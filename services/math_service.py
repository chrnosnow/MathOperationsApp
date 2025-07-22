"""
Pure business logic + persistence.

Each public function
  • validates inputs
  • computes the result
  • logs the request in the database
  • returns the result

All functions are `async` so they interoperate nicely with FastAPI's
async dependency stack. The calculations themselves run synchronously;
if you expect very large workloads, offload to a worker pool.
"""

from __future__ import annotations

import json
import logging
import math
from typing import Any

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from exceptions.exceptions import InvalidInputError
from models.request_log import RequestLog


# --------------------------------------------------------------------------- #
# Internal helpers                                                            #
# --------------------------------------------------------------------------- #
async def _log_request(
    *,
    session: AsyncSession,
    operation: str,
    inputs: dict[str, Any],
    result: Any,
) -> None:
    """
    Persist a RequestLog row.

    Flush only – the surrounding dependency commits.
    """
    entry = RequestLog(
        operation=operation,
        input_data=json.dumps(inputs, separators=(",", ":")),
        result=str(result),
    )
    session.add(entry)
    try:
        await session.flush()
    except SQLAlchemyError as exc:  # noqa: BLE001
        # Do not block the API if logging fails; just warn.
        logging.warning("Failed to log request: %s", exc, exc_info=True)


# --------------------------------------------------------------------------- #
# Public API                                                                  #
# --------------------------------------------------------------------------- #
async def calc_pow(
    *, base: float, exponent: float, session: AsyncSession
) -> float:
    """
    Compute `base ** exponent`.

    Raises
    ------
    InvalidInputError
        If inputs are not finite numbers.
    """
    if not (math.isfinite(base) and math.isfinite(exponent)):
        raise InvalidInputError("Inputs must be finite numbers.")

    try:
        result = math.pow(base, exponent)  # handles floats & ints
    except (OverflowError, ValueError) as exc:  # pragma: no cover
        # Wrap low-level math errors in our domain exception
        raise InvalidInputError(str(exc)) from exc

    await _log_request(
        session=session,
        operation="pow",
        inputs={"base": base, "exponent": exponent},
        result=result,
    )
    return result


async def calc_fibonacci(*, n: int, session: AsyncSession) -> int:
    """
    Compute the n-th Fibonacci number (0-indexed: fib(0)=0, fib(1)=1).

    Uses an O(n) iterative loop, fast enough for n ≤ 10_000 in-process.
    """
    if n < 0:
        raise InvalidInputError("n must be non-negative.")
    if n > 10_000:
        raise InvalidInputError("n must be ≤ 10 000 (safety limit).")

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b

    await _log_request(session=session, operation="fibonacci", inputs={"n": n}, result=a)
    return a


async def calc_factorial(*, n: int, session: AsyncSession) -> int:
    """
    Compute n!  (Uses Python's highly-optimised `math.factorial`.)

    A soft cap at 5 000 avoids blocking the event loop with huge integers;
    bump it higher if you plan to offload heavy work to a background worker.
    """
    if n < 0:
        raise InvalidInputError("n must be non-negative.")
    if n > 5_000:
        raise InvalidInputError("n must be ≤ 5 000 (safety limit).")

    result = math.factorial(n)

    await _log_request(session=session, operation="factorial", inputs={"n": n}, result=result)
    return result
