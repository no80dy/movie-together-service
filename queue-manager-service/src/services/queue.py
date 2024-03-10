import json
import uuid
from functools import lru_cache

from core.config import settings
from fastapi import Depends
from integration.brokers import RabbitMQBroker, get_message_broker
from integration.storages import RedisStorage, get_storage
from schemas.entity import FilmTogether, PartyMember, OutputPartyPayloads
from services.client_id import ClientIDService, get_client_id_service
from services.websocket import WebSocketService, get_websocket_service

AMOUNT_MEMBERS_IN_PARTY = 2
MAX_PARTY_WAITING_TIME = 10 * 60  # 10 мин


class QueueService:
    """queue_id в данном случае есть film_id"""
    def __init__(
        self,
        broker: RabbitMQBroker,
        storage: RedisStorage,
        client_id_service: ClientIDService,
        websocket_service: WebSocketService,
    ):
        self.broker = broker
        self.storage = storage
        self.client_id_service = client_id_service
        self.websocket_service = websocket_service

    async def check_if_client_id_exist(
        self,
        film_together: FilmTogether,
    ) -> bool:
        client_id = self.client_id_service.make_client_id(film_together)
        film_together_dto = film_together.model_dump()
        film_id = str(film_together_dto.get("film_id"))

        queue = await self.storage.get(film_id)
        if not queue:
            return False

        queue = json.loads(queue)
        print(queue)
        members_client_id = [json.loads(member)["client_id"] for member in queue["members"]]
        if client_id in members_client_id:
            return True
        return False

    async def handle_queue(
        self,
        film_together: FilmTogether,

    ) -> str | None:
        client_id = self.client_id_service.make_client_id(film_together)
        film_together_dto = film_together.model_dump()
        film_id = str(film_together_dto.get("film_id"))
        member = PartyMember(
            client_id=client_id,
            user_id=str(film_together_dto.get("user_id")),
            user_agent=film_together_dto.get("user_agent"),
        )

        queue = await self.get_queue(film_id)
        if not queue:
            await self.create_queue(film_id, member)
            return client_id

        await self.add_to_queue(film_id, member)
        queue = json.loads(await self.get_queue(film_id))
        if queue.get("amount") == AMOUNT_MEMBERS_IN_PARTY:
            users_ids = [json.loads(member)["user_id"] for member in queue["members"]]
            party = OutputPartyPayloads(
                film_id=film_id,
                members=users_ids,
            )
            # Отправить в брокер сообщений
            await self.broker.publish_one(party, settings.rabbitmq_queue_name),
            print('Отправил в брокер')

            # TODO Оборвать вебсокет и редиректнуть куда-то, кто будет дерагать ручку пати менеджера каждую секунду о начале
            await self.websocket_service.broadcast(film_id, '__start_watching__')
            # Удалить очередь
            await self.delete_queue(film_id)
            return None

        return client_id

    async def create_queue(
        self,
        queue_id: str,
        member: PartyMember,

    ):
        queue = {"amount": 1, "members": [member.model_dump_json()]}
        await self.storage.set(
            queue_id, json.dumps(queue), MAX_PARTY_WAITING_TIME
        )

    async def get_queue(
        self,
        queue_id: str,

    ):
        return await self.storage.get(queue_id)

    async def add_to_queue(
        self,
        queue_id: str,
        member: PartyMember,
    ):
        queue = json.loads(await self.get_queue(queue_id))
        queue["amount"] += 1
        queue["members"].append(member.model_dump_json())

        await self.storage.set(
            queue_id, json.dumps(queue), MAX_PARTY_WAITING_TIME
        )

    async def remove_from_queue(
        self,
        queue_id: str,
        client_id: str,
    ):
        queue = await self.get_queue(queue_id)
        if queue:
            queue = json.loads(await self.get_queue(queue_id))
            if queue['amount'] > 1:
                queue["amount"] -= 1
                updated_members = [json.loads(member) for member in queue["members"] if json.loads(member)["client_id"] != client_id]
                queue['members'] = updated_members
                await self.storage.set(
                    queue_id, json.dumps(queue), MAX_PARTY_WAITING_TIME
                )
            else:
                await self.delete_queue(queue_id)


    async def delete_queue(
        self,
        queue_id: str
    ):
        await self.storage.delete(queue_id)


@lru_cache
def get_queue_service(
    broker: RabbitMQBroker = Depends(get_message_broker),
    storage: RedisStorage = Depends(get_storage),
    client_id_service: ClientIDService = Depends(get_client_id_service),
    websocket_service: WebSocketService = Depends(get_websocket_service),
):
    return QueueService(broker, storage, client_id_service, websocket_service)
