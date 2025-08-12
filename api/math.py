import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from db import get_session
from deps import get_current_user
from exceptions.exceptions import InvalidInputErr, OverflowErr
from kafka_services.producer import send_request_to_kafka
from schemas.log import RequestLog
from services.math_service import factorial, fibonacci_n, pow_int

# Create a new API router for math-related endpoints
math_router = APIRouter(
    prefix="/math",
    tags=["math"],
    dependencies=[Depends(get_current_user)],  # token required, any role
)


# Calculates the nth Fibonacci number and logs the request.
@math_router.get("/pow", response_model=RequestLog, summary="Integer exponentiation")
async def compute_power(
    x: int = Query(...), y: int = Query(...), session: Session = Depends(get_session)
):
    try:
        result = pow_int(x, y)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    log_entry = RequestLog(
        operation="power",
        parameters=f"x={x}, y={y}",
        result=str(result),
        timestamp=datetime.now(timezone.utc),
    )

    data = log_entry.model_dump(mode="json")
    data["status"] = "received"

    if os.getenv("SERVERLESS") != "TRUE":
        await send_request_to_kafka(data, topic="pow-requests")

    session.add(log_entry)
    session.commit()
    session.refresh(log_entry)
    return log_entry


# Calculates base raised to exponent using
# integer exponentiation and logs the request.
@math_router.get("/fib", response_model=RequestLog, summary="Nth Fibonacci number")
async def compute_fibonacci(
    n: int = Query(..., ge=0), session: Session = Depends(get_session)
):
    try:
        result = fibonacci_n(n)
    except InvalidInputErr as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OverflowErr:
        raise HTTPException(status_code=400, detail="Result exceeds maximum limit")

    log_entry = RequestLog(
        operation="fibonacci",
        parameters=f"n={n}",
        result=str(result),
        timestamp=datetime.now(timezone.utc),
    )

    data = log_entry.model_dump(mode="json")
    data["status"] = "received"

    if os.getenv("SERVERLESS") != "TRUE":
        await send_request_to_kafka(data, topic="fibonacci-requests")

    session.add(log_entry)
    session.commit()
    session.refresh(log_entry)

    return log_entry


# Calculates the factorial of n and logs the request.
@math_router.get(
    "/fact", response_model=RequestLog, summary="Factorial of non-negative integer"
)
async def compute_factorial(
    n: int = Query(..., ge=0), session: Session = Depends(get_session)
):
    try:
        result = factorial(n)
    except InvalidInputErr as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OverflowErr as e:
        raise HTTPException(status_code=400, detail=str(e))

    log_entry = RequestLog(
        operation="factorial",
        parameters=f"n={n}",
        result=str(result),
        timestamp=datetime.now(timezone.utc),
    )

    data = log_entry.model_dump(mode="json")
    data["status"] = "received"

    if os.getenv("SERVERLESS") != "TRUE":
        await send_request_to_kafka(data, topic="factorial-requests")

    session.add(log_entry)
    session.commit()
    session.refresh(log_entry)
    return log_entry
