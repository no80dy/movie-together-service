import uuid

from pydantic import BaseModel


class FilmTogether(BaseModel):
    film_id: uuid.UUID
    user_id: uuid.UUID
    user_agent: str


# class InputWSPayloads(BaseModel):
#     film_id: uuid.UUID
#     client_id: str


class PartyMember(BaseModel):
    user_id: uuid.UUID
    user_agent: str


class OutputPartyPayloads(BaseModel):
    film_id: uuid.UUID
    members: list[PartyMember]
