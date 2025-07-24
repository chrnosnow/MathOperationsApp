from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from schemas.log import RequestLogCreate, RequestLog
from db import get_session

from deps import require_admin


# Apply dependency at router-level because all log routes are admin-only
admin_router = APIRouter(prefix="/logs", tags=["logs"], dependencies=[Depends(require_admin)])


# Returns a welcome message.
@admin_router.get("/")
def read_root():
    return {"message": "Hello, World!"}


# Creates a new log entry. Expects a RequestLogCreate payload.
@admin_router.post("/logs/", response_model=RequestLog)
def create_log(log: RequestLogCreate, session: Session = Depends(get_session)):
    db_log = RequestLog(**log.model_dump())
    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log


# Retrieves all log entries.
@admin_router.get("/logs/", response_model=list[RequestLog])
def read_logs(session: Session = Depends(get_session)):
    return session.exec(select(RequestLog)).all()


# Retrieves a specific log entry by ID.
@admin_router.get("/logs/{log_id}", response_model=RequestLog)
def read_log(log_id: int, session: Session = Depends(get_session)):
    log = session.get(RequestLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


# Updates a log entry by ID. Expects a RequestLogCreate payload.
@admin_router.put("/logs/{log_id}", response_model=RequestLog)
def update_log(log_id: int, log_data: RequestLogCreate,
               session: Session = Depends(get_session)):
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
@admin_router.delete("/logs/{log_id}")
def delete_log(log_id: int, session: Session = Depends(get_session)):
    log = session.get(RequestLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    session.delete(log)
    session.commit()
    return {"ok": True}
