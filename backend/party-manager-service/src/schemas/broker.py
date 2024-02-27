import uuid

from pydantic import BaseModel


class PartyCreationMessage(BaseModel):
	film_id: uuid.UUID
	users_ids: list[uuid.UUID]
