from __future__ import annotations

from datetime import UTC, datetime

from app.integrations.tbank import TBankInvestClient
from app.tasks.celery_app import celery_app


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None

    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)

    return parsed


@celery_app.task(name='tbank.fetch_accounts')
def fetch_accounts(token: str) -> dict:
    return TBankInvestClient(token=token).get_accounts()


@celery_app.task(name='tbank.fetch_portfolio')
def fetch_portfolio(account_id: str, token: str) -> dict:
    return TBankInvestClient(token=token).get_portfolio(account_id=account_id)


@celery_app.task(name='tbank.fetch_operations')
def fetch_operations(
    account_id: str | None = None,
    from_iso: str | None = None,
    to_iso: str | None = None,
) -> dict:
    return TBankInvestClient().get_operations(
        account_id=account_id,
        from_=parse_datetime(from_iso),
        to=parse_datetime(to_iso),
    )
