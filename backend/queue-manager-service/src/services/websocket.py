# import asyncio
# from functools import lru_cache
# from typing import Annotated
#
# from fastapi import Depends
# from integration.brokers import RabbitMQBroker, get_message_broker
# from integration.storages import MongoStorage, get_storage
# from schemas.notifications import PushNotificationSchema
# from schemas.websocket import InputLikeCommentMessage
#
#
# class WebSocketService:
#     mongo_collection_name = "push_notifications"
#     broker_queue_name = "websocket_queue"
#
#     def __init__(self, broker: RabbitMQBroker, storage: MongoStorage):
#         self.broker = broker
#         self.storage = storage
#
#     async def send_notification(self, message: PushNotificationSchema) -> None:
#         await asyncio.gather(
#             self.storage.insert_element(
#                 message.model_dump(mode="json"), self.mongo_collection_name
#             ),
#             self.broker.publish_one(message, self.broker_queue_name),
#         )
#
#     async def handle_message(self, data: dict) -> None:
#         await self.send_notification(
#             PushNotificationSchema(
#                 user_id=data["consumer_id"],
#                 producer_id=data["producer_id"],
#                 comment_id=data["comment_id"],
#             )
#         )
#
#
# @lru_cache
# def get_websocket_service(
#     broker: Annotated[RabbitMQBroker, Depends(get_message_broker)],
#     storage: Annotated[MongoStorage, Depends(get_storage)],
# ):
#     return WebSocketService(broker, storage)
