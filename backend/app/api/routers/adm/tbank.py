from datetime import datetime
from typing import Any

from app.core.security.dependencies import require_admin
from app.schemas.tbank import TBankTaskResponse, TBankTaskStatusResponse
from app.tasks.celery_app import celery_app
from app.tasks.tbank import fetch_accounts, fetch_operations, fetch_portfolio
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Query, status

router = APIRouter(
    prefix='/tbank',
    tags=['T-Bank'],
    dependencies=[Depends(require_admin)],
)


@router.post('/accounts/fetch', status_code=status.HTTP_202_ACCEPTED)
def enqueue_accounts_fetch(
    user_token: str = Query(..., description='TOKEN клиента Т банка'),
) -> TBankTaskResponse:
    task = fetch_accounts.delay(user_token)
    return TBankTaskResponse(task_id=task.id, status=task.status)


@router.post('/portfolio/fetch', status_code=status.HTTP_202_ACCEPTED)
def enqueue_portfolio_fetch(
    account_id: str = Query(..., description='ID аккаунта от Т банка '),
    user_token: str = Query(..., description='TOKEN клиента Т банка'),
) -> TBankTaskResponse:
    task = fetch_portfolio.delay(account_id=account_id, token=user_token)
    return TBankTaskResponse(task_id=task.id, status=task.status)


@router.post('/operations/fetch', status_code=status.HTTP_202_ACCEPTED)
def enqueue_operations_fetch(
    account_id: str = Query(..., description='ID аккаунта от Т банка '),
    user_token: str = Query(..., description='TOKEN клиента Т банка'),
    from_dt: datetime | None = Query(None, alias='from'),
    to_dt: datetime | None = Query(None, alias='to'),
) -> TBankTaskResponse:
    task = fetch_operations.delay(
        account_id=account_id,
        token=user_token,
        from_iso=from_dt.isoformat() if from_dt else None,
        to_iso=to_dt.isoformat() if to_dt else None,
    )
    return TBankTaskResponse(task_id=task.id, status=task.status)


@router.get('/tasks/{task_id}')
def get_tbank_task_status(task_id: str) -> TBankTaskStatusResponse:
    task = AsyncResult(task_id, app=celery_app)
    result: Any | None = None
    error: str | None = None

    if task.successful():
        result = task.result
    elif task.failed():
        error = str(task.result)

    return TBankTaskStatusResponse(
        task_id=task.id,
        status=task.status,
        result=result,
        error=error,
    )
