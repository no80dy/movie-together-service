import asyncio
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from integration.brokers import RabbitMQBroker, get_message_broker
from integration.storages import RedisStorage, get_storage

from schemas.entity import FilmTogether
from schemas.websocket import InputLikeCommentMessage


class QueueService:
    def __init__(self, broker: RabbitMQBroker, storage: RedisStorage):
        self.broker = broker
        self.storage = storage

    # async def send_notification(self, message: PushNotificationSchema) -> None:
    #     await asyncio.gather(
    #         self.storage.insert_element(
    #             message.model_dump(mode="json"), self.mongo_collection_name
    #         ),
    #         self.broker.publish_one(message, self.broker_queue_name),
    #     )
    #
    # async def handle_message(self, data: dict) -> None:
    #     await self.send_notification(
    #         PushNotificationSchema(
    #             user_id=data["consumer_id"],
    #             producer_id=data["producer_id"],
    #             comment_id=data["comment_id"],
    #         )
    #     )

    async def handle_queue(
            self,
            film_together: FilmTogether
    ) -> None:
        await asyncio.sleep(1)
        print(film_together)


@lru_cache
def get_queue_service(
    broker: RabbitMQBroker = Depends(get_message_broker),
    storage: RedisStorage = Depends(get_storage),
):
    return QueueService(broker, storage)
