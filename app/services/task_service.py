from sqlalchemy.orm import Session

from app.db.models import Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session,task_data: TaskCreate,user_id: int):
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


def get_task(db: Session,task_id: int,user_id: int):
    return (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user_id
        )
        .first()
    )


def get_tasks(db: Session,user_id: int):
    return (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .all()
    )


def update_task(db: Session,task_id: int,task_data: TaskUpdate,user_id: int):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user_id
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


def delete_task(db: Session,task_id: int,user_id: int):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user_id
        )
        .first()
    )

    if not task:
        return None

    db.delete(task)
    db.commit()
    return task