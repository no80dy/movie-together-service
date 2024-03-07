import json
from functools import lru_cache

from core.config import settings
from fastapi import Depends
from integration.brokers import RabbitMQBroker, get_message_broker
from integration.storages import RedisStorage, get_storage
from schemas.entity import FilmTogether, OutputPartyPayloads
from services.client_id import ClientIDService, get_client_id_service
from services.websocket import WebSocketService, get_websocket_service

AMOUNT_MEMBERS_IN_PARTY = 10
MAX_PARTY_WAITING_TIME = 10 * 60  # 10 мин


class QueueService:
    def __init__(
        self,
        broker: RabbitMQBroker,
        storage: RedisStorage,
        client_id_service: ClientIDService = Depends(get_client_id_service),
    ):
        self.broker = broker
        self.storage = storage
        self.client_id_service = client_id_service

    async def check_if_client_id_exist(
        self, film_together: FilmTogether
    ) -> bool:
        client_id = self.client_id_service.make_client_id(film_together)
        film_together_dto = film_together.model_dump()
        film_id = str(film_together_dto.get("film_id"))

        queue = await self.storage.get(film_id)
        if not queue:
            return False

        queue = json.loads(queue)
        members = queue["members"]
        members_client_id = [member["client_id"] for member in members]
        print(members_client_id)
        if client_id in members_client_id:
            return True
        return False

    async def handle_queue(
        self,
        film_together: FilmTogether,
        websocket_service: WebSocketService = Depends(get_websocket_service),
    ) -> int:
        client_id = self.client_id_service.make_client_id(film_together)
        film_together_dto = film_together.model_dump()
        film_id = str(film_together_dto.get("film_id"))
        user = {
            "user_id": str(film_together_dto.get("user_id")),
            "user_agent": film_together_dto.get("user_agent"),
            "client_id": client_id,
        }

        queue = await self.storage.get(film_id)

        if not queue:
            queue = {"amount": 1, "members": [user]}
            await self.storage.set(
                film_id, json.dumps(queue), MAX_PARTY_WAITING_TIME
            )
            return queue["amount"]

        queue = json.loads(queue)
        if queue.get("amount") == AMOUNT_MEMBERS_IN_PARTY - 1:
            party = OutputPartyPayloads(
                film_id=film_id,
                members=queue.get("members"),
            )
            # TODO Отправить в брокер сообщений
            await self.broker.publish_one(party, settings.rabbitmq_queue_name),

            await self.storage.delete("film_id")
            # TODO Оборвать вебсокет и редиректнуть куда-то

        else:
            queue["amount"] += 1
            queue["members"].append(user)

            await self.storage.set(
                film_id, json.dumps(queue), MAX_PARTY_WAITING_TIME
            )
            return queue["amount"]

            # TODO Подключится к уже открытому вебсокету. Отправить данные в вебсокет

    async def create_queue(self):
        pass

    async def add_to_queue(self):
        pass

    async def remove_from_queue(self):
        pass


@lru_cache
def get_queue_service(
    broker: RabbitMQBroker = Depends(get_message_broker),
    storage: RedisStorage = Depends(get_storage),
):
    return QueueService(broker, storage)
