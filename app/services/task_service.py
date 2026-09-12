from datetime import datetime, timezone
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models import Task
from app.schemas.task import TaskCreate, TaskPriority, TaskStatus, TaskUpdate


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


def get_tasks(
    db: Session,
    user_id: int,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    query = db.query(Task).filter(Task.user_id == user_id)

    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern),
            )
        )

    # Handle sorting
    sort_attr = getattr(Task, sort_by, Task.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_attr.asc())
    else:
        query = query.order_by(sort_attr.desc())

    return query.offset(skip).limit(limit).all()


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


def get_task_stats(db: Session, user_id: int):
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    now = datetime.now(timezone.utc)

    total_tasks = len(tasks)
    pending_tasks = sum(1 for t in tasks if t.status == TaskStatus.pending or t.status == "pending")
    in_progress_tasks = sum(1 for t in tasks if t.status == TaskStatus.in_progress or t.status == "in_progress")
    completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.completed or t.status == "completed")
    cancelled_tasks = sum(1 for t in tasks if t.status == TaskStatus.cancelled or t.status == "cancelled")

    high_priority_tasks = sum(1 for t in tasks if t.priority == TaskPriority.high or t.priority == "high")
    medium_priority_tasks = sum(1 for t in tasks if t.priority == TaskPriority.medium or t.priority == "medium")
    low_priority_tasks = sum(1 for t in tasks if t.priority == TaskPriority.low or t.priority == "low")

    overdue_tasks = sum(
        1 for t in tasks
        if t.due_date is not None
        and t.due_date.tzinfo is not None and t.due_date < now
        and t.status not in (TaskStatus.completed, "completed", TaskStatus.cancelled, "cancelled")
    )

    return {
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks,
        "cancelled_tasks": cancelled_tasks,
        "high_priority_tasks": high_priority_tasks,
        "medium_priority_tasks": medium_priority_tasks,
        "low_priority_tasks": low_priority_tasks,
        "overdue_tasks": overdue_tasks,
    }


def clear_completed_tasks(db: Session, user_id: int):
    tasks_to_delete = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.status == TaskStatus.completed,
        )
        .all()
    )
    count = len(tasks_to_delete)
    for task in tasks_to_delete:
        db.delete(task)
    db.commit()
    return count


def bulk_delete_tasks(db: Session, task_ids: list[int], user_id: int):
    tasks_to_delete = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.id.in_(task_ids),
        )
        .all()
    )
    count = len(tasks_to_delete)
    for task in tasks_to_delete:
        db.delete(task)
    db.commit()
    return count


def bulk_update_task_status(db: Session, task_ids: list[int], status: TaskStatus, user_id: int):
    tasks_to_update = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.id.in_(task_ids),
        )
        .all()
    )
    for task in tasks_to_update:
        task.status = status
    db.commit()
    for task in tasks_to_update:
        db.refresh(task)
    return tasks_to_update