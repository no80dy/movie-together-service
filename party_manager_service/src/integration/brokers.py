from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from faststream.rabbit import RabbitBroker
from pydantic import BaseModel

from .rabbitmq import get_rabbitmq


class IBroker(ABC):
    @abstractmethod
    async def publish_one(self, message: BaseModel, queue: str) -> None:
        pass

    @abstractmethod
    async def publish_many(
        self, messages: list[BaseModel], queue: str
    ) -> None:
        pass


class RabbitMQBroker(IBroker):
    def __init__(self, broker: RabbitBroker):
        self.broker = broker

    async def publish_one(self, message: BaseModel, queue: str) -> None:
        await self.broker.publish(message=message, queue=queue)

    async def publish_many(
        self, messages: list[BaseModel], queue: str
    ) -> None:
        for message in messages:
            await self.broker.publish(message=message, queue=queue)


@lru_cache
def get_message_broker(
    broker: Annotated[RabbitBroker, Depends(get_rabbitmq)],
) -> RabbitMQBroker:
    return RabbitMQBroker(broker)
