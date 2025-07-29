import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.admin_logs import admin_router
from api.auth import auth_router
from api.math import math_router
from core.startup_seed import seed_admin
from db import create_db_and_tables
from metrics.metrics import metrics_router

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

        created = seed_admin()
        if created:
            logger.info("Default admin user/role created (user: admin / admin1234)")
        else:
            logger.info("Admin user and role already present; no changes made.")
    except Exception as e:
        logger.exception("Error creating database tables.")
        raise e
    yield
    logger.info("Shutting down app...")


# Create FastAPI app with lifespan for setup and teardown
app = FastAPI(lifespan=lifespan)

# Register all API endpoints with the app
app.include_router(auth_router)  # authentication endpoints
app.include_router(admin_router)  # admin-only endpoints
app.include_router(math_router)  # user endpoints
app.include_router(metrics_router) # metrics endpoint


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
