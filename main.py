from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import create_db_and_tables
from api.endpoints import router


#test for database connection and creation
#to run use python -m uvicorn main:app --reload --port 8080
# Define lifespan event handler for FastAPI
@asynccontextmanager
async def lifespan(app):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)


