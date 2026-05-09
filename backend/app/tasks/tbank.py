from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from app.infrastructure.db.database import async_session_maker
from app.integrations.tbank import TBankInvestClient
from app.repositories.tbank_connection import TBankIntegrationRepositoryPostgres
from app.tasks.celery_app import celery_app


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None

    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)

    return parsed


@celery_app.task(name='tbank.fetch_accounts')
def fetch_accounts(conn_id: int) -> dict:
    return asyncio.run(_fetch_accounts(conn_id))


async def _fetch_accounts(connection_id: int) -> dict:
    async with async_session_maker() as session:
        repo = TBankIntegrationRepositoryPostgres(session=session)
        conn = await repo.get_by_id(connection_id)

        if conn is None:
            raise ValueError(f'TBank connection {connection_id} not found')

        token = conn.encrypted_api_token
    return TBankInvestClient(token=token).get_accounts()


@celery_app.task(name='tbank.fetch_portfolio')
def fetch_portfolio(account_id: str, token: str) -> dict:
    return TBankInvestClient(token=token).get_portfolio(account_id=account_id)


@celery_app.task(name='tbank.fetch_operations')
def fetch_operations(
    account_id: str,
    token: str,
    from_iso: str | None = None,
    to_iso: str | None = None,
) -> dict:
    return TBankInvestClient(token=token).get_operations(
        account_id=account_id,
        from_=parse_datetime(from_iso),
        to=parse_datetime(to_iso),
    )
