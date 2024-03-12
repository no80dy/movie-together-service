import uuid

from pydantic import BaseModel


class FilmTogether(BaseModel):
    film_id: uuid.UUID
    user_id: uuid.UUID
    user_agent: str


class PartyMember(BaseModel):
    client_id: str
    user_id: uuid.UUID
    user_agent: str


class OutputPartyPayloads(BaseModel):
    film_id: uuid.UUID
    users_ids: list[uuid.UUID]
