from typing import Annotated

from fastapi import Depends
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitRouter
from faststream.rabbit.fastapi import RabbitRouter
import logging
from core.config import settings
from schemas.broker import PartyCreationMessage
from services.broker import PartyManagerService, get_party_manager_service
from .auth import security_jwt

from faststream.rabbit.fastapi import RabbitRouter, Logger

router = RabbitRouter(
    host=settings.rabbitmq_host,
    port=settings.rabbitmq_port,
    login=settings.rabbitmq_login,
    password=settings.rabbitmq_password,
)
# apps = FastStream(broker)
# router = RabbitRouter(prefix="prefix_")


@router.subscriber("film_queue")
async def create_party(
    party_creation_message: PartyCreationMessage,
    logger: Logger,
    party_manager_service: Annotated[
        PartyManagerService, Depends(get_party_manager_service)
    ],
):
    print("start create party", party_creation_message)
    logger.info("after_startup")
    result = await party_manager_service.create_party(party_creation_message)
    # return {"redirect_url": f"http://localhost/party-manager-service/api/v1/stream/{result}"}


# router = RabbitRouter("amqp://user:rabbitmq@rabbitmq:5672/")


def broker():
    return router.broker

# @router.subscriber("film_queue")
# async def create_party(msg, logger: Logger):
#     print("after_startup")
#     logging.info("after_startup")
#     logger.info("after_startup")
#     print(msg)


# @router.after_startup
# async def test():
#     print("after_startup")
#     logging.info("after_startup")
#     try:
#         await router.broker.publish("Hello!", "film_queue")
#     except Exception as e:
#         print("err", e)

@router.get("/hello")
async def hello_http(broker: Annotated[RabbitBroker, Depends(broker)]):
    await broker.publish("Hello, Rabbit!", "test")
    return "Hello, HTTP!"
