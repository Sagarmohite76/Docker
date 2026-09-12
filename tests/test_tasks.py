import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.db.database import get_db
from app.db.models import User
from app.main import app

# Create in-memory SQLite database for testing
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
    # Create test user with ID 1
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
    assert data["priority"] == "high"
    task_id = data["id"]

    # Get single task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_tasks_filtering_and_search():
    client.post("/tasks/", json={"title": "Fix bug in login", "status": "in_progress", "priority": "high"})
    client.post("/tasks/", json={"title": "Write unit tests", "status": "pending", "priority": "medium"})
    client.post("/tasks/", json={"title": "Deploy to staging", "status": "completed", "priority": "low"})

    # Filter by status
    res = client.get("/tasks/?status=in_progress")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Fix bug in login"

    # Filter by priority
    res = client.get("/tasks/?priority=high")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Fix bug in login"

    # Search keyword
    res = client.get("/tasks/?search=unit")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Write unit tests"


def test_task_stats_summary():
    client.post("/tasks/", json={"title": "Task 1", "status": "pending", "priority": "high"})
    client.post("/tasks/", json={"title": "Task 2", "status": "completed", "priority": "medium"})

    res = client.get("/tasks/stats/summary")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_tasks"] == 2
    assert stats["pending_tasks"] == 1
    assert stats["completed_tasks"] == 1
    assert stats["high_priority_tasks"] == 1
    assert stats["medium_priority_tasks"] == 1


def test_update_and_complete_task():
    res = client.post("/tasks/", json={"title": "Old Title", "status": "pending", "priority": "low"})
    task_id = res.json()["id"]

    # Quick status update
    res = client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"

    # Quick complete endpoint
    res = client.patch(f"/tasks/{task_id}/complete")
    assert res.status_code == 200
    assert res.json()["status"] == "completed"

    # Full update (PUT)
    res = client.put(f"/tasks/{task_id}", json={
        "title": "New Updated Title",
        "description": "Updated description",
        "status": "completed",
        "priority": "high",
    })
    assert res.status_code == 200
    assert res.json()["title"] == "New Updated Title"
    assert res.json()["priority"] == "high"


def test_bulk_operations_and_clear_completed():
    t1 = client.post("/tasks/", json={"title": "Task 1", "status": "pending"}).json()["id"]
    t2 = client.post("/tasks/", json={"title": "Task 2", "status": "pending"}).json()["id"]
    t3 = client.post("/tasks/", json={"title": "Task 3", "status": "pending"}).json()["id"]

    # Bulk status update to completed
    res = client.post("/tasks/bulk-status", json={"task_ids": [t1, t2], "status": "completed"})
    assert res.status_code == 200
    updated_tasks = res.json()
    assert len(updated_tasks) == 2
    assert all(t["status"] == "completed" for t in updated_tasks)

    # Clear completed tasks
    res = client.delete("/tasks/completed/clear")
    assert res.status_code == 200
    assert res.json()["deleted_count"] == 2

    # Bulk delete remaining task
    res = client.post("/tasks/bulk-delete", json={"task_ids": [t3]})
    assert res.status_code == 200
    assert res.json()["deleted_count"] == 1
