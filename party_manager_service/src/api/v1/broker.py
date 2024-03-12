from typing import Annotated

from core.config import settings
from fastapi import Depends
from faststream.rabbit.fastapi import RabbitRouter
from schemas.broker import PartyCreationMessage
from services.broker import PartyManagerService, get_party_manager_service

router = RabbitRouter(
    host=settings.rabbitmq_host,
    port=settings.rabbitmq_port,
    login=settings.rabbitmq_login,
    password=settings.rabbitmq_password,
)


@router.subscriber("film_queue")
async def create_party(
    party_creation_message: PartyCreationMessage,
    party_manager_service: Annotated[
        PartyManagerService, Depends(get_party_manager_service)
    ],
):
    # print("start create party", party_creation_message)
    await party_manager_service.create_party(party_creation_message)
