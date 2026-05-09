from app.models.tbank_connections import TBankConnection
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TBankIntegrationRepositoryPostgres:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, encrypted_token: str, name: str):
        obj = TBankConnection(
            user_id=user_id,
            encrypted_api_token=encrypted_token,
            name=name,
        )
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by_user_id(self, user_id: int):
        query = select(TBankConnection).where(TBankConnection.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, connection_id: int):
        query = select(TBankConnection).where(
            TBankConnection.id == connection_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, connection) -> None:
        await self.session.delete(connection)
        await self.session.commit()
