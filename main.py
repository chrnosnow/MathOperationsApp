# python
from fastapi import FastAPI
from db import create_db_and_tables
from contextlib import asynccontextmanager


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