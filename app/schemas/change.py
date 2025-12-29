from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.db.models import ChangeStatus


class ChangeItemCreate(BaseModel):
    key: str = Field(min_length=1, max_length=200)
    old_value: str = Field(min_length=1, max_length=500)
    new_value: str = Field(min_length=1, max_length=500)


class ChangeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default=None, max_length=5000)
    environment: str = Field(pattern="^(staging|prod)$")
    created_by: str = Field(min_length=2, max_length=100)
    items: list[ChangeItemCreate] = Field(min_length=1)


class ChangeItemRead(BaseModel):
    id: UUID
    key: str
    old_value: str
    new_value: str

    model_config = {"from_attributes": True}

class ChangeRead(BaseModel):
    id: UUID
    title: str
    description: str | None
    environment: str
    status: ChangeStatus
    created_by: str
    created_at: datetime
    updated_at: datetime
    items: list[ChangeItemRead]

    model_config = {"from_attributes": True}


class ApproveRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=200)
