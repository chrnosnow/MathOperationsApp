from fastapi import FastAPI, Depends
from db import create_db_and_tables
from db import get_session
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from models.log import RequestLog


#test for database connection and creation
#to run use python -m uvicorn main:app --reload --port 8080
# Define lifespan event handler for FastAPI
@asynccontextmanager
async def lifespan(app):
    # Create database tables at startup
    create_db_and_tables()
    print("Database tables created successfully.")  # Confirm execution
    yield

# Create FastAPI application instance with lifespan handler
app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/logs/", response_model=RequestLog)
def create_log(log: RequestLog, session: Session = Depends(get_session)):
    session.add(log)
    session.commit()
    session.refresh(log)
    return log

@app.get("/logs/", response_model=list[RequestLog])
def read_logs(session: Session = Depends(get_session)):
    logs = session.exec(select(RequestLog)).all()
    return logs
