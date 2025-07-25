"""
Business-logic layer for all math operations.
"""

import math
from functools import lru_cache
from typing import Final

from exceptions.exceptions import InvalidInputErr, OverflowErr

# A very relaxed overflow limit so that we fail gracefully instead of
# freezing the process. Needs to be adjusted for
# specific deployment constraints.
MAX_ABSOLUTE_VALUE: Final[int] = 10**12


# ───────────────────────── power ──────────────────────────────────────────
@lru_cache(maxsize=256)
def pow_int(base: int, exponent: int) -> int:
    """
    Integer exponentiation using exponentiation by squaring
    (O(log n) multiplications).

    The call is cached so repeated identical requests are served from an
    in-memory dictionary.
    """
    result: int = 1
    b: int = base
    e: int = exponent

    while e:
        if e & 1:  # e is odd
            result *= b
        b *= b
        e >>= 1  # floor-divide by 2

    _guard_overflow(result)
    return result


# ───────────────────────── fibonacci ──────────────────────────────────────
@lru_cache(maxsize=1024)
def fibonacci_n(n: int) -> int:
    """
    Fast doubling method (O(log n)).  Much faster than naïve recursion.

    Returns Fₙ where F₀ = 0, F₁ = 1.
    Raises
    ------
    InvalidInputErr  – if n < 0
    OverflowErr    – if Fₙ would exceed service limits
    """

    if n < 0:
        raise InvalidInputErr("n must be ≥ 0")

    def _fib(k: int) -> tuple[int, int]:
        if k == 0:
            return 0, 1

        a, b = _fib(k >> 1)
        c = a * ((b << 1) - a)  # c = F(m) * (2*F(m+1) - F(m)) = F(2m)
        d = a * a + b * b  # d = F(m)^2 + F(m+1)^2 = F(2m+1)
        return (c, d) if k & 1 == 0 else (d, c + d)

    value = _fib(n)[0]
    _guard_overflow(value)
    return value


# ───────────────────────── factorial ──────────────────────────────────────
@lru_cache(maxsize=512)
def factorial(n: int) -> int:
    """
    Compute n! using Python’s built-in math.factorial (fast C code),
    with a safety check on the result size.

    Caching the wrapper means repeated calls (e.g. 5! multiple times)
    still hit our in-memory cache.
    """
    if n < 0:
        raise InvalidInputErr("n must be ≥ 0")

    # math.factorial is implemented in C and is very fast
    result = math.factorial(n)

    # guard against absurdly large results
    if abs(result) > MAX_ABSOLUTE_VALUE:
        raise OverflowErr(
            f"Result too large (>|{MAX_ABSOLUTE_VALUE}|); refusing to compute."
        )
    return result


# ───────────────────────── helpers ────────────────────────────────────────
def _guard_overflow(value: int) -> None:
    """
    Lightweight protection against requests that would allocate absurd
    amounts of memory when serialised to JSON.
    """
    if abs(value) > MAX_ABSOLUTE_VALUE:
        raise OverflowErr(
            f"Result too large (>|{MAX_ABSOLUTE_VALUE}|).  "
            "Refuse to compute—protecting the service."
        )
