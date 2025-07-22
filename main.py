from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from api.endpoints import router as math_router
# from db import init_db
from exceptions.exceptions import MathServiceError
from schemas.operations import ErrorResponse
from db import create_db_and_tables
from contextlib import asynccontextmanager


# #test for database connection and creation
# #to run use python -m uvicorn main:app --reload --port 8080
# # Define lifespan event handler for FastAPI
# @asynccontextmanager
# async def lifespan(app):
#     # Create database tables at startup
#     create_db_and_tables()
#     print("Database tables created successfully.")  # Confirm execution
#     yield
#
# # Create FastAPI application instance with lifespan handler
# app = FastAPI(lifespan=lifespan)
#
#
# @app.get("/")
# def read_root():
#     return {"message": "Hello, World!"}


"""
FastAPI application factory.

• Creates tables on startup via `init_db`.
• Maps domain exceptions ➜ HTTP 400 with a uniform payload.
"""




app = FastAPI(
    title="Math Microservice",
    version="1.0.0",
    description="Async FastAPI service for pow, Fibonacci and factorial.",
)


# --------------------------------------------------------------------------- #
# Startup / shutdown                                                          #
# --------------------------------------------------------------------------- #
# @app.on_event("startup")
# async def _startup() -> None:
#     await init_db()
@asynccontextmanager
async def lifespan(app):
    # Create database tables at startup
    create_db_and_tables()
    print("Database tables created successfully.")  # Confirm execution
    yield

# Create FastAPI application instance with lifespan handler
app = FastAPI(lifespan=lifespan)

# --------------------------------------------------------------------------- #
# Exception handling                                                          #
# --------------------------------------------------------------------------- #
@app.exception_handler(MathServiceError)
async def _handle_math_errors(
    request: Request, exc: MathServiceError  # noqa: D401
) -> JSONResponse:
    """
    Convert domain exceptions to 400 Bad Request with `ErrorResponse` payload.
    """
    payload = ErrorResponse(exc.__str__()).model_dump()
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=payload,
    )


# --------------------------------------------------------------------------- #
# Routers                                                                     #
# --------------------------------------------------------------------------- #
app.include_router(math_router)
