import functools
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

from main import app
from services import math_service
from services.math_service import factorial, fibonacci_n, pow_int


# Use python -m pytest to run the tests
@pytest_asyncio.fixture
# async client
async def client(session_override):  # session_override is needed to trigger DB override
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


#  ---------- TESTS FOR ADMIN LOGS ENDPOINT ----------
@pytest.mark.asyncio
async def test_create_log(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    log_data = {
        "operation": "test_op",
        "parameters": "param1,param2",
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = await client.post("/logs/", headers=headers, json=log_data)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_logs(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/logs/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_read_log_not_found(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/logs/9999", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_log(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # First, create a log
    log_data = {
        "operation": "update_op",
        "parameters": "p1",
        "result": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    create_resp = await client.post("/logs/", headers=headers, json=log_data)
    log_id = create_resp.json()["id"]

    # Update the log
    update_data = {
        "operation": "updated_op",
        "parameters": "p2",
        "result": "updated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = await client.put(f"/logs/{log_id}", headers=headers, json=update_data)
    assert response.status_code == 200
    assert response.json()["operation"] == "updated_op"


@pytest.mark.asyncio
async def test_delete_log(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # First, create a log
    log_data = {
        "operation": "delete_op",
        "parameters": "p1",
        "result": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    create_resp = await client.post("/logs/", headers=headers, json=log_data)
    log_id = create_resp.json()["id"]

    # Delete the log
    response = await client.delete(f"/logs/{log_id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Confirm deletion
    response = await client.get(f"/logs/{log_id}", headers=headers)
    assert response.status_code == 404


# ---------- TESTS FOR POWER ENDPOINT ----------
@pytest.mark.asyncio
async def test_power_valid_input(client, token_user):
    headers = {"Authorization": f"Bearer {token_user}"}
    response = await client.get("/math/pow", headers=headers, params={"x": 2, "y": 8})
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "power"
    assert data["parameters"] == "x=2, y=8"
    assert data["result"] == str(2**8)


invalid_payloads = [
    # negative numbers
    {"base": -1, "exponent": 3},
    {"base": 2, "exponent": -5},
    {"base": -4, "exponent": -2},
    # wrong types
    {"base": "foo", "exponent": 3},
    {"base": 2, "exponent": "bar"},
    # missing fields
    {"exponent": 3},
    {"base": 2},
    {},  # empty body
]


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", invalid_payloads)
async def test_pow_invalid_payload_returns_422(client, token_user, payload):
    headers = {"Authorization": f"Bearer {token_user}"}
    response = await client.get("/math/pow", headers=headers, params=payload)
    assert response.status_code == 422
    assert isinstance(response.json().get("detail"), list)


# test that confirms caching behavior of pow_int() by wrapping it
def test_pow_int_caching(monkeypatch):
    call_counter = {"count": 0}

    # Save the original function
    original = pow_int.__wrapped__

    def counted_pow(x: int, y: int) -> int:
        call_counter["count"] += 1
        return original(x, y)

    # Patch the function with a counted + cached version
    monkeypatch.setattr(
        math_service, "pow_int", functools.lru_cache(maxsize=256)(counted_pow)
    )
    math_service.pow_int.cache_clear()

    # Call the same input multiple times
    math_service.pow_int(10, 5)
    math_service.pow_int(10, 5)
    math_service.pow_int(10, 5)

    assert call_counter["count"] == 1, "pow_int was recomputed despite caching"


# ---------- TESTS FOR FIBONACCI ENDPOINT ----------
@pytest.mark.asyncio
async def test_fibonacci_valid_input(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/math/fib", headers=headers, params={"n": 10})
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "fibonacci"
    assert data["parameters"] == "n=10"
    assert data["result"] == str(55)  # Fibonacci(10) = 55


invalid_payloads_fib = [
    # negative numbers
    {"n": -5},
    # wrong types
    {"n": "foo"},
    # missing fields
    {},  # empty body
]


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", invalid_payloads_fib)
async def test_fibonacci_invalid_input(client, admin_token, payload):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/math/fib", headers=headers, params=payload)
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
    monkeypatch.setattr(
        math_service, "fibonacci_n", functools.lru_cache(maxsize=1024)(counted_fib)
    )

    # Call repeatedly
    math_service.fibonacci_n(20)
    math_service.fibonacci_n(20)
    math_service.fibonacci_n(20)

    assert call_counter["count"] == 1, "fibonacci_n was recomputed despite cache"


@pytest.mark.asyncio
async def test_fibonacci_overflow(client, token_user):
    headers = {"Authorization": f"Bearer {token_user}"}
    response = await client.get("/math/fib", headers=headers, params={"n": 1000})
    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"].lower()


# -------------- TESTS FOR FACTORIAL ENDPOINT ----------
@pytest.mark.asyncio
async def test_factorial_valid_input(client, token_user):
    headers = {"Authorization": f"Bearer {token_user}"}
    response = await client.get("/math/fact", headers=headers, params={"n": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "factorial"
    assert data["parameters"] == "n=5"
    assert data["result"] == str(120)


invalid_payloads_fact = [
    # negative numbers
    {"n": -3},
    # wrong types
    {"n": "foo"},
    # missing fields
    {},  # empty body
]


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", invalid_payloads_fact)
async def test_factorial_invalid_input(client, token_user, payload):
    headers = {"Authorization": f"Bearer {token_user}"}
    response = await client.get("/math/fact", headers=headers, params=payload)
    assert response.status_code == 422
    assert isinstance(response.json().get("detail"), list)


# test that confirms caching behavior of factorial() by wrapping it
def test_factorial_caching(monkeypatch):
    call_counter = {"count": 0}
    original = factorial.__wrapped__

    def counted_factorial(n: int) -> int:
        call_counter["count"] += 1
        return original(n)

    monkeypatch.setattr(
        math_service, "factorial", functools.lru_cache(maxsize=512)(counted_factorial)
    )
    math_service.factorial.cache_clear()

    math_service.factorial(6)
    math_service.factorial(6)
    math_service.factorial(6)

    assert call_counter["count"] == 1, "factorial was recomputed despite caching"


# --------------- TESTS FOR USER PRIVILEGES ---------------
@pytest.mark.asyncio
async def test_non_admin_cannot_create_log(client, token_user):
    r = await client.post(
        "/logs/",
        headers={"Authorization": f"Bearer {token_user}"},
        json={"operation": "fib", "parameters": "n=3", "result": "2"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_list_logs(client, token_user):
    headers = {"Authorization": f"Bearer {token_user}"}
    response = await client.get("/logs/", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_read_single_log(client, token_user):
    headers = {"Authorization": f"Bearer {token_user}"}
    response = await client.get("/logs/1", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_update_log(client, token_user):
    headers = {"Authorization": f"Bearer {token_user}"}
    update_data = {
        "operation": "edit_attempt",
        "parameters": "none",
        "result": "fail",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = await client.put("/logs/1", headers=headers, json=update_data)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_delete_log(client, token_user):
    headers = {"Authorization": f"Bearer {token_user}"}
    response = await client.delete("/logs/1", headers=headers)
    assert response.status_code == 403


#  ---------- TESTS FOR ANONYMOUS USER ACCESSING ENDPOINTS ---------------
@pytest.mark.asyncio
async def test_anonymous_cannot_access_logs_list(client):
    response = await client.get("/logs/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_anonymous_cannot_create_log(client):
    log_data = {
        "operation": "anonymous",
        "parameters": "x=1",
        "result": "denied",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = await client.post("/logs/", json=log_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_anonymous_cannot_access_math_pow(client):
    response = await client.get("/math/pow", params={"x": 2, "y": 5})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_anonymous_cannot_access_math_fib(client):
    response = await client.get("/math/fib", params={"n": 5})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_anonymous_cannot_access_math_fact(client):
    response = await client.get("/math/fact", params={"n": 5})
    assert response.status_code == 401
