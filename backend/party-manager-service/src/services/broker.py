import uuid

from typing import Annotated
from functools import lru_cache
from fastapi import Depends

from schemas.broker import PartyCreationMessage
from integration.storages import IStorage, get_storage


class PartyManagerService:
	def __init__(self, storage: IStorage):
		self.storage = storage

	async def create_party(self, party_creation_message: PartyCreationMessage):
		await self.storage.insert_element(
			{
				"party_id": uuid.uuid4(),
				"film_id": party_creation_message.film_id,
				"users_ids": party_creation_message.users_ids
			},
			"parties"
		)


@lru_cache
def get_party_manager_service(
	storage: Annotated[IStorage, Depends(get_storage)]
) -> PartyManagerService:
	return PartyManagerService(storage)
