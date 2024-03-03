from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Annotated, Any

from core.config import settings
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from .mongodb import get_mongo_client


class IStorage(ABC):
    @abstractmethod
    async def find_element_by_properties(
        self, properties: dict, collection_name: str
    ) -> Any:
        pass

    @abstractmethod
    async def find_elements_by_properties(
        self, properties: dict, collection_name: str
    ) -> list[Any]:
        pass

    @abstractmethod
    async def insert_element(
        self, element: dict, collection_name: str
    ) -> None:
        pass

    @abstractmethod
    async def update_element(
        self, find_property: dict, update_property: dict, collection_name: str
    ) -> None:
        pass


class MongoStorage(IStorage):
    def __init__(self, client: AsyncIOMotorClient, database_name: str):
        self.database_client = client[database_name]

    async def find_element_by_properties(
        self, properties: dict, collection_name: str
    ) -> Any:
        return await self.database_client[collection_name].find_one(properties)

    async def find_elements_by_properties(
        self, properties: dict, collection_name: str
    ) -> list[Any]:
        return (
            await self.database_client[collection_name]
            .find(properties)
            .to_list(length=None)
        )

    async def insert_element(
        self, element: dict, collection_name: str
    ) -> None:
        await self.database_client[collection_name].insert_one(element)

    async def insert_elements(
        self, elements: list[dict], collection_name: str
    ) -> None:
        await self.database_client[collection_name].insert_many(elements)

    async def update_element(
        self, find_property: dict, update_property: dict, collection_name: str
    ) -> None:
        await self.database_client[collection_name].update_one(
            find_property, update_property
        )


@lru_cache
def get_storage(
    client: Annotated[AsyncIOMotorClient, Depends(get_mongo_client)]
) -> IStorage:
    return MongoStorage(client, settings.mongodb_database_name)