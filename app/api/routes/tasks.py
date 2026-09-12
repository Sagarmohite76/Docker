from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import (
    create_task,
    get_task,
    get_tasks,
    update_task,
    delete_task,
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
)
def get_all_tasks(
    db: Session = Depends(get_db),
):
    return get_tasks(
        db=db,
        user_id=CURRENT_USER_ID,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
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


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
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


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
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