from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


class TBankTaskResponse(APIModel):
    task_id: str = Field(..., description='Celery task id')
    status: str = Field(..., description='Initial Celery task status')


class TBankTaskStatusResponse(TBankTaskResponse):
    result: Any | None = Field(None, description='Task result payload')
    error: str | None = Field(None, description='Task failure text')
