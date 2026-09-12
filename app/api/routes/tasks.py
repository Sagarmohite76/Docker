from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.task import (
    TaskBulkDeleteRequest,
    TaskBulkDeleteResponse,
    TaskBulkStatusUpdate,
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatsResponse,
    TaskStatus,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.task_service import (
    bulk_delete_tasks,
    bulk_update_task_status,
    clear_completed_tasks,
    create_task,
    delete_task,
    get_task,
    get_task_stats,
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
    summary="Get all tasks with filtering, search, sorting and pagination",
)
def get_all_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status", description="Filter by task status"),
    priority_filter: TaskPriority | None = Query(default=None, alias="priority", description="Filter by task priority"),
    search: str | None = Query(default=None, description="Search keyword in title or description"),
    skip: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Number of items to return"),
    sort_by: str = Query(default="created_at", description="Field to sort by (created_at, due_date, priority, title)"),
    sort_order: str = Query(default="desc", description="Sort direction (asc, desc)"),
    db: Session = Depends(get_db),
):
    return get_tasks(
        db=db,
        user_id=CURRENT_USER_ID,
        status=status_filter,
        priority=priority_filter,
        search=search,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/stats/summary",
    response_model=TaskStatsResponse,
    summary="Get task statistics summary for current user",
)
def get_task_stats_summary(
    db: Session = Depends(get_db),
):
    return get_task_stats(
        db=db,
        user_id=CURRENT_USER_ID,
    )


@router.delete(
    "/completed/clear",
    response_model=TaskBulkDeleteResponse,
    summary="Delete all completed tasks for current user",
)
def clear_completed(
    db: Session = Depends(get_db),
):
    deleted_count = clear_completed_tasks(
        db=db,
        user_id=CURRENT_USER_ID,
    )
    return {
        "deleted_count": deleted_count,
        "message": f"Successfully deleted {deleted_count} completed task(s)",
    }


@router.post(
    "/bulk-delete",
    response_model=TaskBulkDeleteResponse,
    summary="Delete multiple tasks by IDs",
)
def bulk_delete(
    payload: TaskBulkDeleteRequest,
    db: Session = Depends(get_db),
):
    deleted_count = bulk_delete_tasks(
        db=db,
        task_ids=payload.task_ids,
        user_id=CURRENT_USER_ID,
    )
    return {
        "deleted_count": deleted_count,
        "message": f"Successfully deleted {deleted_count} task(s)",
    }


@router.post(
    "/bulk-status",
    response_model=list[TaskResponse],
    summary="Update status for multiple tasks",
)
def bulk_update_status(
    payload: TaskBulkStatusUpdate,
    db: Session = Depends(get_db),
):
    return bulk_update_task_status(
        db=db,
        task_ids=payload.task_ids,
        status=payload.status,
        user_id=CURRENT_USER_ID,
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
    summary="Replace existing task details (Full update)",
)
def replace_existing_task(
    task_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    update_data = TaskUpdate(**task_data.model_dump())
    task = update_task(
        db=db,
        task_id=task_id,
        task_data=update_data,
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
    summary="Update existing task details (Partial update)",
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
    summary="Update status of a specific task",
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
    summary="Mark task status as completed",
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