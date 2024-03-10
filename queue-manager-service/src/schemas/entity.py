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

# class InputWSPayloads(BaseModel):
#     film_id: uuid.UUID
#     client_id: str


# Для сервиса party-manager-service
# class OutputPartyMember(BaseModel):
#     user_id: uuid.UUID


class OutputPartyPayloads(BaseModel):
    film_id: uuid.UUID
    members: list[uuid.UUID]
