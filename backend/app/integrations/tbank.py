from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from t_tech.invest import (
    Client,
    GetOperationsByCursorRequest,
    OperationState,
    OperationType,
)

NANO_SCALE = Decimal('1000000000')


class TBankInvestConfigError(RuntimeError):
    pass


def quotation_to_decimal(value: Any | None) -> Decimal | None:
    if value is None:
        return None

    units = getattr(value, 'units', 0)
    nano = getattr(value, 'nano', 0)
    return Decimal(units) + (Decimal(nano) / NANO_SCALE)


def decimal_to_str(value: Decimal | None) -> str | None:
    if value is None:
        return None

    return str(value.normalize())


def money_to_payload(value: Any | None) -> dict[str, str | None]:
    return {
        'amount': decimal_to_str(quotation_to_decimal(value)),
        'currency': getattr(value, 'currency', None),
    }


def enum_to_name(value: Any | None) -> str | None:
    if value is None:
        return None

    return getattr(value, 'name', str(value))


def datetime_to_str(value: datetime | None) -> str | None:
    if value is None:
        return None

    return value.isoformat()


class TBankInvestClient:
    def __init__(self, token: str) -> None:
        token_value = token
        self._token = token_value

    def get_accounts(self) -> dict[str, Any]:
        with Client(self._token) as client:
            response = client.users.get_accounts()

        accounts = [
            {
                'id': account.id,
                'name': account.name,
                'type': enum_to_name(account.type),
                'status': enum_to_name(account.status),
                'opened_date': datetime_to_str(getattr(account, 'opened_date', None)),
                'closed_date': datetime_to_str(getattr(account, 'closed_date', None)),
            }
            for account in response.accounts
        ]
        return {'count': len(accounts), 'accounts': accounts}

    def get_portfolio(self, account_id: str) -> dict[str, Any]:
        account_id = account_id

        with Client(self._token) as client:
            portfolio = client.operations.get_portfolio(account_id=account_id)

        return {
            'account_id': account_id,
            'totals': {
                'portfolio': money_to_payload(portfolio.total_amount_portfolio),
                'shares': money_to_payload(portfolio.total_amount_shares),
                'bonds': money_to_payload(portfolio.total_amount_bonds),
                'etf': money_to_payload(portfolio.total_amount_etf),
                'currencies': money_to_payload(portfolio.total_amount_currencies),
                'expected_yield': decimal_to_str(quotation_to_decimal(portfolio.expected_yield)),
            },
            'positions': [self._position_to_payload(position) for position in portfolio.positions],
        }

    def get_operations(
        self,
        *,
        account_id: str,
        from_: datetime | None = None,
        to: datetime | None = None,
        page_limit: int = 100,
    ) -> dict[str, Any]:
        account_id = account_id
        items: list[dict[str, Any]] = []
        cursor = ''

        with Client(self._token) as client:
            while True:
                response = client.operations.get_operations_by_cursor(
                    GetOperationsByCursorRequest(
                        account_id=account_id,
                        from_=from_,
                        to=to,
                        cursor=cursor,
                        limit=page_limit,
                        operation_types=[
                            OperationType.OPERATION_TYPE_BUY,
                            OperationType.OPERATION_TYPE_SELL,
                        ],
                        state=OperationState.OPERATION_STATE_EXECUTED,
                        without_commissions=True,
                        without_trades=False,
                        without_overnights=True,
                    )
                )
                items.extend(self._operation_to_payload(item) for item in response.items)

                if not response.has_next:
                    break
                cursor = response.next_cursor

        return {'account_id': account_id, 'count': len(items), 'operations': items}

    @staticmethod
    def _position_to_payload(position: Any) -> dict[str, Any]:
        return {
            'ticker': getattr(position, 'ticker', None),
            'figi': getattr(position, 'figi', None),
            'instrument_uid': getattr(position, 'instrument_uid', None),
            'instrument_type': getattr(position, 'instrument_type', None),
            'quantity': decimal_to_str(quotation_to_decimal(getattr(position, 'quantity', None))),
            'quantity_lots': decimal_to_str(
                quotation_to_decimal(getattr(position, 'quantity_lots', None))
            ),
            'average_position_price': money_to_payload(
                getattr(position, 'average_position_price', None)
            ),
            'current_price': money_to_payload(getattr(position, 'current_price', None)),
            'expected_yield': decimal_to_str(
                quotation_to_decimal(getattr(position, 'expected_yield', None))
            ),
            'blocked': getattr(position, 'blocked', False),
        }

    @staticmethod
    def _operation_to_payload(operation: Any) -> dict[str, Any]:
        trades_info = getattr(operation, 'trades_info', None)
        trades = []
        if trades_info is not None:
            trades = [
                {
                    'num': trade.num,
                    'date': datetime_to_str(trade.date),
                    'quantity': trade.quantity,
                    'price': money_to_payload(trade.price),
                }
                for trade in getattr(trades_info, 'trades', [])
            ]

        return {
            'id': operation.id,
            'parent_operation_id': operation.parent_operation_id,
            'name': operation.name,
            'date': datetime_to_str(operation.date),
            'type': enum_to_name(operation.type),
            'description': operation.description,
            'state': enum_to_name(operation.state),
            'ticker': getattr(operation, 'ticker', None),
            'figi': operation.figi,
            'instrument_uid': operation.instrument_uid,
            'instrument_type': operation.instrument_type,
            'position_uid': operation.position_uid,
            'payment': money_to_payload(operation.payment),
            'price': money_to_payload(operation.price),
            'commission': money_to_payload(operation.commission),
            'quantity': operation.quantity,
            'quantity_done': operation.quantity_done,
            'trades': trades,
        }
