import uuid
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from integration.storages import IStorage, get_storage
from schemas.broker import PartyCreationMessage


class PartyManagerService:
    def __init__(self, storage: IStorage):
        self.storage = storage

    async def create_party(self, party_creation_message: PartyCreationMessage):
        party_id = uuid.uuid4()
        await self.storage.insert_element(
            {
                "party_id": str(party_id),
                "film_id": str(party_creation_message.film_id),
                "users_ids": [
                    str(user_id)
                    for user_id in party_creation_message.users_ids
                ],
                "messages": [],
            },
            "parties",
        )
        return party_id

    async def find_party_by_id(self, party_id: uuid.UUID) -> dict:
        try:
            return await self.storage.find_element_by_properties(
                {"party_id": str(party_id)}, "parties"
            )
        except Exception as e:
            print(e)

    async def find_party_id_by_user_id(
        self, user_id: uuid.UUID
    ) -> dict | None:
        try:
            return await self.storage.find_element_by_properties(
                {"users_ids": {"$in": [str(user_id)]}}, "parties"
            )
        except Exception as e:
            print(e)


@lru_cache
def get_party_manager_service(
    storage: Annotated[IStorage, Depends(get_storage)]
) -> PartyManagerService:
    return PartyManagerService(storage)
