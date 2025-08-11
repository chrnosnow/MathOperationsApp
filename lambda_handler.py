"""
Lambda entry-point.

AWS Lambda will import this file and look for the `handler` object.
Mangum converts API-Gateway events to ASGI calls so our FastAPI
app (defined in main.py) runs unmodified.
"""

from mangum import Mangum

from main import app  # the FastAPI() instance you already have

handler = Mangum(app)  # ← Lambda will call this
