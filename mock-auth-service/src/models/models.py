from uuid import UUID
from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: UUID
    username: str = Field(max_length=255)
    password: str = Field(max_length=255)
