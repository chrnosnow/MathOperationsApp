from prometheus_client import Counter
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

metrics_router = APIRouter()


@metrics_router.get("/metrics", tags=["Metrics"])
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Count total calls to each math operation
math_calls_total = Counter(
    "math_calls_total",
    "Total number of math function calls",
    ["operation", "source"]
)
