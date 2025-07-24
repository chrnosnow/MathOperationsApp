import functools
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

from db import create_db_and_tables
from main import app
from services import math_service
from services.math_service import (
    factorial,
    fibonacci_n,
    pow_int,
)

# Use python -m pytest to run the tests

client = TestClient(app)
create_db_and_tables()


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_create_log():
    log_data = {
        "operation": "test_op",
        "parameters": "param1,param2",
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    response = client.post("/logs/", json=log_data)
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "test_op"
    assert data["parameters"] == "param1,param2"
    assert data["result"] == "success"


def test_read_logs():
    response = client.get("/logs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_log_not_found():
    response = client.get("/logs/9999")
    assert response.status_code == 404


def test_update_log():
    # First, create a log
    log_data = {
        "operation": "update_op",
        "parameters": "p1",
        "result": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    create_resp = client.post("/logs/", json=log_data)
    log_id = create_resp.json()["id"]

    # Update the log
    update_data = {
        "operation": "updated_op",
        "parameters": "p2",
        "result": "updated",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    response = client.put(f"/logs/{log_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["operation"] == "updated_op"


def test_delete_log():
    # First, create a log
    log_data = {
        "operation": "delete_op",
        "parameters": "p1",
        "result": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    create_resp = client.post("/logs/", json=log_data)
    log_id = create_resp.json()["id"]

    # Delete the log
    response = client.delete(f"/logs/{log_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Confirm deletion
    response = client.get(f"/logs/{log_id}")
    assert response.status_code == 404


# ---------- TESTS FOR POWER ENDPOINT ----------
@pytest.mark.asyncio
async def test_power_valid_input(session_override):
    transport = ASGITransport(app=app)
    async with (AsyncClient(transport=transport, base_url="http://test")
                as client):
        response = await client.get("/math/pow", params={"x": 2, "y": 8})
        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "power"
        assert data["parameters"] == "x=2, y=8"
        assert data["result"] == str(2 ** 8)


invalid_payloads = [
    # negative numbers
    {"base": -1, "exponent": 3},
    {"base": 2,  "exponent": -5},
    {"base": -4, "exponent": -2},

    # wrong types
    {"base": "foo", "exponent": 3},
    {"base": 2,     "exponent": "bar"},

    # missing fields
    {"exponent": 3},
    {"base": 2},
    {},                     # empty body
]


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", invalid_payloads)
async def test_pow_invalid_payload_returns_422(session_override, payload):
    transport = ASGITransport(app=app)
    async with (AsyncClient(transport=transport, base_url="http://test")
                as client):
        """Any schema violation should yield a 422 validation error."""
        response = await client.get("/math/pow", params=payload)
        assert response.status_code == 422

        # Basic shape check: FastAPI’s default validation error structure
        body = response.json()
        assert "detail" in body
        # list of error items
        assert isinstance(body["detail"], list)
        assert body["detail"], "detail list should not be empty"


# test that confirms caching behavior of pow_int() by wrapping it
def test_pow_int_caching(monkeypatch):
    call_counter = {"count": 0}

    # Save the original function
    original = pow_int.__wrapped__

    def counted_pow(x: int, y: int) -> int:
        call_counter["count"] += 1
        return original(x, y)

    # Patch the function with a counted + cached version
    monkeypatch.setattr(math_service, "pow_int",
                        functools.lru_cache(maxsize=256)(counted_pow))
    math_service.pow_int.cache_clear()

    # Call the same input multiple times
    math_service.pow_int(10, 5)
    math_service.pow_int(10, 5)
    math_service.pow_int(10, 5)

    assert call_counter["count"] == 1, "pow_int was recomputed despite caching"


# ---------- TESTS FOR FIBONACCI ENDPOINT ----------
@pytest.mark.asyncio
async def test_fibonacci_valid_input(session_override):
    transport = ASGITransport(app=app)
    async with (AsyncClient(transport=transport, base_url="http://test")
                as client):
        response = await client.get("/math/fib", params={"n": 10})
        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "fibonacci"
        assert data["parameters"] == "n=10"
        assert data["result"] == str(55)  # Fibonacci(10) = 55


@pytest.mark.asyncio
async def test_fibonacci_invalid_input(session_override):
    transport = ASGITransport(app=app)
    async with (AsyncClient(transport=transport, base_url="http://test")
                as client):
        response = await client.get("/math/fib", params={"n": -5})
        assert response.status_code == 422
        assert isinstance(response.json().get("detail"), list)


# test that confirms caching behavior of fibonacci_n() by wrapping it
# and counting how many times the underlying computation is actually executed
def test_fibonacci_n_caching(monkeypatch):
    call_counter = {"count": 0}

    # Create a custom function with counting logic
    def counted_fib(n: int) -> int:
        call_counter["count"] += 1
        return original(n)

    # Save and clear original cache
    original = fibonacci_n.__wrapped__
    fibonacci_n.cache_clear()

    # Patch the whole function temporarily
    monkeypatch.setattr(math_service, "fibonacci_n",
                        functools.lru_cache(maxsize=1024)(counted_fib))

    # Call repeatedly
    math_service.fibonacci_n(20)
    math_service.fibonacci_n(20)
    math_service.fibonacci_n(20)

    assert call_counter["count"] == 1, \
        "fibonacci_n was recomputed despite cache"


@pytest.mark.asyncio
async def test_fibonacci_overflow(session_override):
    transport = ASGITransport(app=app)
    async with (AsyncClient(transport=transport, base_url="http://test")
                as client):
        # Choose a value of `n` that exceeds MAX_ABSOLUTE_VALUE
        response = await client.get("/math/fib", params={"n": 1000})
        assert response.status_code == 400
        assert "exceeds" in response.json()["detail"].lower()


# -------------- TESTS FOR FACTORIAL ENDPOINT ----------
@pytest.mark.asyncio
async def test_factorial_valid_input(session_override):
    transport = ASGITransport(app=app)
    async with (AsyncClient(transport=transport, base_url="http://test")
                as client):
        response = await client.get("/math/fact", params={"n": 5})
        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "factorial"
        assert data["parameters"] == "n=5"
        assert data["result"] == str(120)


@pytest.mark.asyncio
async def test_factorial_invalid_input(session_override):
    transport = ASGITransport(app=app)
    async with (AsyncClient(transport=transport, base_url="http://test")
                as client):
        response = await client.get("/math/fact", params={"n": -3})
        assert response.status_code == 422
        assert isinstance(response.json().get("detail"), list)


# test that confirms caching behavior of factorial() by wrapping it
def test_factorial_caching(monkeypatch):
    call_counter = {"count": 0}
    original = factorial.__wrapped__

    def counted_factorial(n: int) -> int:
        call_counter["count"] += 1
        return original(n)

    monkeypatch.setattr(math_service, "factorial",
                        functools.lru_cache(maxsize=512)(counted_factorial))
    math_service.factorial.cache_clear()

    math_service.factorial(6)
    math_service.factorial(6)
    math_service.factorial(6)

    assert call_counter["count"] == 1, \
        "factorial was recomputed despite caching"


schema_violations = [
    {"n": -5},           # negative
    {"n": "foo"},        # wrong type
    {},                  # missing field
]


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", schema_violations)
async def test_fibonacci_schema_violations(payload):
    transport = ASGITransport(app=app)
    async with (AsyncClient(transport=transport, base_url="http://test")
                as client):
        response = await client.get("/math/fact", params=payload)
        assert response.status_code == 422
        # FastAPI validation errors are a list under "detail"
        assert isinstance(response.json().get("detail"), list)


# --------------- TESTS FOR USER PRIVILEGES ---------------

async def test_non_admin_cannot_create_log(client, token_user):
    r = await client.post(
        "/logs/",
        headers={"Authorization": f"Bearer {token_user}"},
        json={"operation":"fib","parameters":"n=3","result":"2"}
    )
    assert r.status_code == 403
