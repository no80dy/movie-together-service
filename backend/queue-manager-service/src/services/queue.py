import hashlib
import json
from functools import lru_cache

from fastapi import Depends
from integration.brokers import RabbitMQBroker, get_message_broker
from integration.storages import RedisStorage, get_storage

from core.config import settings
from schemas.entity import FilmTogether, OutputPartyPayloads


AMOUNT_MEMBERS_IN_PARTY = 10
MAX_PARTY_WAITING_TIME = 10 * 60  # 10 мин


class QueueService:
    def __init__(self, broker: RabbitMQBroker, storage: RedisStorage):
        self.broker = broker
        self.storage = storage

    @staticmethod
    async def _make_client_id(
            film_together: FilmTogether
    ) -> str:
        """Создание уникального идентификатора для клиента."""
        film_together_dto = film_together.model_dump()
        film_id = film_together_dto.get('film_id')
        user_id = film_together_dto.get('user_id')
        user_agent = film_together_dto.get('user_agent')

        client_id_raw = str(film_id) + str(user_id) + str(user_agent)
        return hashlib.sha256(client_id_raw.encode('utf-8')).hexdigest()

    async def check_if_client_id_exist(
            self,
            film_together: FilmTogether
    ) -> bool:
        client_id = await self._make_client_id(film_together)
        film_together_dto = FilmTogether.model_dump()
        film_id = film_together_dto.get('film_id')

        queue = json.loads(await self.storage.get(film_id))
        if not queue:
            return False
        members = queue['members']
        members_client_id = [member['client_id'] for member in members]
        if client_id in members_client_id:
            return True
        return False

    async def handle_queue(
            self,
            film_together: FilmTogether
    ) -> int:
        if self.check_if_client_id_exist(film_together):
            # TODO Редирект на тот же вебсокет
            pass

        client_id = await self._make_client_id(film_together)
        film_together_dto = film_together.model_dump()
        film_id = film_together_dto.get('film_id')
        user = {
            'user_id': film_together_dto.get('user_id'),
            'user_agent': film_together_dto.get('user_agent'),
            'client_id': client_id
        }

        queue = json.loads(await self.storage.get(film_id))

        if not queue:
            queue = {
                'amount': 1,
                'members': [user]
            }
            await self.storage.set(film_id, queue, MAX_PARTY_WAITING_TIME)
            return queue['amount']

            # TODO Открыть вебсокет для передачи данных

        if queue.get('amount') == AMOUNT_MEMBERS_IN_PARTY - 1:
            party = OutputPartyPayloads(
                film_id=film_id,
                members=queue.get('members'),
            )
            # TODO Отправить в брокер сообщений
            await self.broker.publish_one(party, settings.rabbitmq_queue_name),

            await self.storage.delete('film_id')
            # TODO Оборвать вебсокет и редиректнуть куда-то

        else:
            queue['amount'] += 1
            queue['members'].append(user)
            await self.storage.set(film_id, queue, MAX_PARTY_WAITING_TIME)
            return queue['amount']

            # TODO Подключится к уже открытому вебсокету. Отправить данные в вебсокет


@lru_cache
def get_queue_service(
    broker: RabbitMQBroker = Depends(get_message_broker),
    storage: RedisStorage = Depends(get_storage),
):
    return QueueService(broker, storage)
