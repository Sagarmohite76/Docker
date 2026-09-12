from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskStatus, TaskStatusUpdate, TaskUpdate
from app.services.task_service import (
    create_task,
    delete_task,
    get_task,
    get_tasks,
    update_task,
    update_task_status,
)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)

# Temporary user ID until authentication is implemented
CURRENT_USER_ID = 1


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_new_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    return create_task(
        db=db,
        task_data=task_data,
        user_id=CURRENT_USER_ID,
    )


@router.get(
    "/",
    response_model=list[TaskResponse],
    summary="Get all tasks (optional status filter)",
)
def get_all_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status", description="Filter tasks by status"),
    db: Session = Depends(get_db),
):
    return get_tasks(
        db=db,
        user_id=CURRENT_USER_ID,
        status=status_filter,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Retrieve a single task by ID",
)
def get_single_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = get_task(
        db=db,
        task_id=task_id,
        user_id=CURRENT_USER_ID,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Full update of a task",
)
def replace_existing_task(
    task_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    update_payload = TaskUpdate(**task_data.model_dump())
    task = update_task(
        db=db,
        task_id=task_id,
        task_data=update_payload,
        user_id=CURRENT_USER_ID,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partial update of task details",
)
def update_existing_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = update_task(
        db=db,
        task_id=task_id,
        task_data=task_data,
        user_id=CURRENT_USER_ID,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Update task status",
)
def update_existing_task_status(
    task_id: int,
    status_payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
):
    task = update_task_status(
        db=db,
        task_id=task_id,
        status=status_payload.status,
        user_id=CURRENT_USER_ID,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Mark task as completed",
)
def mark_task_completed(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = update_task_status(
        db=db,
        task_id=task_id,
        status=TaskStatus.completed,
        user_id=CURRENT_USER_ID,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
def delete_existing_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = delete_task(
        db=db,
        task_id=task_id,
        user_id=CURRENT_USER_ID,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return None