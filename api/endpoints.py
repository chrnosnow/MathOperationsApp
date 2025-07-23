from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from models.log import RequestLogCreate, RequestLog
from db import get_session
from services.math_service import pow_int, fibonacci_n, factorial
from exceptions.exceptions import MathServiceErr, InvalidInputErr, OverflowErr

router = APIRouter()

# Returns a welcome message.
@router.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Creates a new log entry. Expects a RequestLogCreate payload.
@router.post("/logs/", response_model=RequestLog)
def create_log(log: RequestLogCreate, session: Session = Depends(get_session)):
    db_log = RequestLog(**log.model_dump())
    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log

# Retrieves all log entries.
@router.get("/logs/", response_model=list[RequestLog])
def read_logs(session: Session = Depends(get_session)):
    return session.exec(select(RequestLog)).all()

# Retrieves a specific log entry by ID.
@router.get("/logs/{log_id}", response_model=RequestLog)
def read_log(log_id: int, session: Session = Depends(get_session)):
    log = session.get(RequestLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

# Updates a log entry by ID. Expects a RequestLogCreate payload.
@router.put("/logs/{log_id}", response_model=RequestLog)
def update_log(log_id: int, log_data: RequestLogCreate, session: Session = Depends(get_session)):
    log = session.get(RequestLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    for key, value in log_data.dict(exclude_unset=True).items():
        setattr(log, key, value)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log

# Deletes a log entry by ID.
@router.delete("/logs/{log_id}")
def delete_log(log_id: int, session: Session = Depends(get_session)):
    log = session.get(RequestLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    session.delete(log)
    session.commit()
    return {"ok": True}


# ----------------- MATH ENDPOINTS -------------------------------
# Calculates the nth Fibonacci number and logs the request.
@router.get("/math/pow", response_model=RequestLog, summary="Integer exponentiation")
def compute_power(x: int = Query(...), y: int = Query(...), session: Session = Depends(get_session)):
    try:
        result = pow_int(x, y)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    log_entry = RequestLog(
        operation="power",
        parameters=f"x={x}, y={y}",
        result=str(result),
        timestamp=datetime.now(timezone.utc)
    )
    session.add(log_entry)
    session.commit()
    session.refresh(log_entry)
    return log_entry

# Calculates base raised to exponent using integer exponentiation and logs the request.
@router.get("/math/fib", response_model=RequestLog, summary="Nth Fibonacci number")
def compute_fibonacci(n: int = Query(..., ge=0), session: Session = Depends(get_session)):
    try:
        result = fibonacci_n(n)
    except InvalidInputErr as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OverflowErr as e:
        raise HTTPException(status_code=400, detail="Result exceeds maximum limit")

    log_entry = RequestLog(
        operation="fibonacci",
        parameters=f"n={n}",
        result=str(result),
        timestamp=datetime.now(timezone.utc)
    )

    session.add(log_entry)
    session.commit()
    session.refresh(log_entry)

    return log_entry

# Calculates the factorial of n and logs the request.
@router.get("/math/fact", response_model=RequestLog, summary="Factorial of non-negative integer")
def compute_factorial(n: int = Query(..., ge=0), session: Session = Depends(get_session)):
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
        timestamp=datetime.now(timezone.utc)
    )

    session.add(log_entry)
    session.commit()
    session.refresh(log_entry)
    return log_entry
