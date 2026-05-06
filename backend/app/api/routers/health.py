from __future__ import annotations

from typing import Any

from app.infrastructure.db.database import engine
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter(prefix='/health', tags=['Healthcheck'])


@router.get('/live')
async def liveness_probe() -> dict[str, str]:
    return {'status': 'ok'}


@router.get('/ready', response_model=None)
async def readiness_probe(request: Request) -> dict[str, Any] | JSONResponse:
    checks = {
        'database': await _check_database(),
        'redis': await _check_redis(request),
    }
    is_ready = all(checks.values())
    body = {
        'status': 'ready' if is_ready else 'not_ready',
        'checks': checks,
    }

    if is_ready:
        return body

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=body,
    )


async def _check_database() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
    except Exception:
        return False

    return True


async def _check_redis(request: Request) -> bool:
    try:
        await request.app.state.redis.ping()
    except Exception:
        return False

    return True
