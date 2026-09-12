from sqlalchemy.orm import Session

from app.db.models import Task
from app.schemas.task import TaskCreate, TaskStatus, TaskUpdate


def create_task(db: Session, task_data: TaskCreate, user_id: int):
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int, user_id: int):
    return (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user_id,
        )
        .first()
    )


def get_tasks(db: Session, user_id: int, status: TaskStatus | None = None):
    query = db.query(Task).filter(Task.user_id == user_id)
    if status:
        query = query.filter(Task.status == status)
    return query.all()


def update_task(db: Session, task_id: int, task_data: TaskUpdate, user_id: int):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user_id,
        )
        .first()
    )

    if not task:
        return None

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


def update_task_status(db: Session, task_id: int, status: TaskStatus, user_id: int):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user_id,
        )
        .first()
    )

    if not task:
        return None

    task.status = status
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, user_id: int):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user_id,
        )
        .first()
    )

    if not task:
        return None

    db.delete(task)
    db.commit()
    return task