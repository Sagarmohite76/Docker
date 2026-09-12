import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.db.database import get_db
from app.db.models import User
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    user = User(
        id=1,
        name="Test User",
        email="testuser@example.com",
        password_hash="hashedpassword123",
    )
    db.add(user)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_and_get_task():
    payload = {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "status": "pending",
        "priority": "high",
    }
    response = client.post("/tasks/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["status"] == "pending"
    task_id = data["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_tasks_status_filter():
    client.post("/tasks/", json={"title": "Task 1", "status": "pending"})
    client.post("/tasks/", json={"title": "Task 2", "status": "completed"})

    res = client.get("/tasks/?status=pending")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task 1"


def test_update_and_complete_task():
    res = client.post("/tasks/", json={"title": "Task 1", "status": "pending"})
    task_id = res.json()["id"]

    # Patch status
    res = client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"

    # Mark complete
    res = client.patch(f"/tasks/{task_id}/complete")
    assert res.status_code == 200
    assert res.json()["status"] == "completed"

    # Full update PUT
    res = client.put(f"/tasks/{task_id}", json={
        "title": "Updated Task 1",
        "status": "completed",
        "priority": "high",
    })
    assert res.status_code == 200
    assert res.json()["title"] == "Updated Task 1"
    assert res.json()["priority"] == "high"


def test_delete_task():
    res = client.post("/tasks/", json={"title": "To be deleted"})
    task_id = res.json()["id"]

    res = client.delete(f"/tasks/{task_id}")
    assert res.status_code == 204

    res = client.get(f"/tasks/{task_id}")
    assert res.status_code == 404
