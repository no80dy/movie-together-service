from typing import Annotated

from fastapi import Depends
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitRouter
from faststream.rabbit.fastapi import RabbitRouter

from core.config import settings
from schemas.broker import PartyCreationMessage
from services.broker import PartyManagerService, get_party_manager_service
from .auth import security_jwt

from faststream.rabbit.fastapi import RabbitRouter
router = RabbitRouter(
    host=settings.rabbitmq_host,
    port=settings.rabbitmq_port,
    login=settings.rabbitmq_login,
    password=settings.rabbitmq_password,
)
# apps = FastStream(broker)
# router = RabbitRouter(prefix="prefix_")


# @router.subscriber("films_queues")
# async def create_party(
#     party_creation_message: PartyCreationMessage,
#     party_manager_service: Annotated[
#         PartyManagerService, Depends(get_party_manager_service)
#     ],
# ):
#     print("start create party", party_creation_message)
#     result = await party_manager_service.create_party(party_creation_message)
    # return {"redirect_url": f"http://localhost/party-manager-service/api/v1/stream/{result}"}



@router.subscriber("film_queue")
async def create_party(msg):
    print(msg)

