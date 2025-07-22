from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from datetime import datetime, timezone

class RequestLogCreate(BaseModel):
    # Primary key column, auto-incremented
    id: int | None = Field(default=None, primary_key=True)
    # Name of the operation performed (e.g., 'pow', 'fibonacci')
    operation: str
    # Parameters used for the operation, stored as a string
    parameters: str
    # Result of the operation, stored as a string
    result: str
    # Timestamp when the request was logged, defaults to current UTC time
    timestamp: datetime = Field(default_factory=datetime.now(timezone.utc))

class RequestLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    operation: str
    parameters: str
    result: str
    timestamp: datetime = Field(default_factory=datetime.now(timezone.utc))

