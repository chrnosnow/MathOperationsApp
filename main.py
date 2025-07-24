from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.math import math_router
from db import create_db_and_tables
from api.admin_logs import admin_router
import logging
import uvicorn

# test for database connection and creation
# to run use python -m uvicorn main:app --reload --port 8080

# Configure logger for Uvicorn
logger = logging.getLogger("uvicorn.error")

# Define lifespan event handler for FastAPI
# to initialize and clean up resources


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up app and initializing database...")
    try:
        create_db_and_tables()  # Create database schema if not already present
        logger.info("Database tables created or already exist.")

    except Exception as e:
        logger.exception("Error creating database tables.")
        raise e
    yield
    logger.info("Shutting down app...")

# Create FastAPI app with lifespan for setup and teardown
app = FastAPI(lifespan=lifespan)

# Register all API endpoints with the app
app.include_router(admin_router)    # admin-only endpoints
app.include_router(math_router)     # user endpoints


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
