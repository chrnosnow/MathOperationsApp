from fastapi.testclient import TestClient
from main import app
from datetime import datetime

#install pytest
#use python -m pytest to see the tests

# def test_read_root():
    # client = TestClient(app)
    # response = client.get("/")
    # assert response.status_code == 200
    # assert response.json() == {"message": "Hello, World!"}


client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_create_log():
    log_data = {
        "operation": "test_op",
        "parameters": "param1,param2",
        "result": "success",
        "timestamp": datetime.utcnow().isoformat()
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
        "timestamp": datetime.utcnow().isoformat()
    }
    create_resp = client.post("/logs/", json=log_data)
    log_id = create_resp.json()["id"]

    # Update the log
    update_data = {
        "operation": "updated_op",
        "parameters": "p2",
        "result": "updated",
        "timestamp": datetime.utcnow().isoformat()
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
        "timestamp": datetime.utcnow().isoformat()
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




