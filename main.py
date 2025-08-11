import logging
from contextlib import asynccontextmanager

import asyncio

import uvicorn
from fastapi import FastAPI

from api.admin_logs import admin_router
from api.auth import auth_router
from api.math import math_router
from core.startup_seed import seed_admin
from db import create_db_and_tables
from kafka_services.consumer import consume_kafka
from metrics.metrics import metrics_router

from kafka_services import producer


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
        logger.info("Prometheus metrics available at http://localhost:9090")
        logger.info("Swagger UI available at http://localhost:8080/docs")

        # Start the Kafka consumer thread
        asyncio.create_task(consume_kafka())
        logger.info(" Kafka async consumer task started")

        # Start the Kafka producer
        await producer.init_kafka_producer()

    except Exception as e:
        logger.exception("Error creating database tables.")
        raise e
    yield
    logger.info("Shutting down app...")
    await producer.stop_kafka_producer()


# Create FastAPI app with lifespan for setup and teardown
app = FastAPI(lifespan=lifespan)

# Register all API endpoints with the app
app.include_router(auth_router)  # authentication endpoints
app.include_router(admin_router)  # admin-only endpoints
app.include_router(math_router)  # user endpoints
app.include_router(metrics_router)  # metrics endpoint

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
