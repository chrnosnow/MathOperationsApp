from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models.log import RequestLogCreate, RequestLog
from db import get_session

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Hello, World!"}


@router.post("/logs/", response_model=RequestLog)
def create_log(log: RequestLogCreate, session: Session = Depends(get_session)):
    db_log = RequestLog(**log.dict())
    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log

@router.get("/logs/", response_model=list[RequestLog])
def read_logs(session: Session = Depends(get_session)):
    return session.exec(select(RequestLog)).all()

@router.get("/logs/{log_id}", response_model=RequestLog)
def read_log(log_id: int, session: Session = Depends(get_session)):
    log = session.get(RequestLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

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

@router.delete("/logs/{log_id}")
def delete_log(log_id: int, session: Session = Depends(get_session)):
    log = session.get(RequestLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    session.delete(log)
    session.commit()
    return {"ok": True}
