from celery.result import AsyncResult
from fastapi import APIRouter, Depends

from celery_app import celery_app
from core.auth import require_scope
from schemas import TaskResult

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}", response_model=TaskResult)
async def get_task(task_id: str, _: object = Depends(require_scope("task:read"))):

    result = AsyncResult(task_id, app=celery_app)

    return TaskResult(status=result.status, result=result.result)
