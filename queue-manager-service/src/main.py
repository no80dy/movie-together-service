from contextlib import asynccontextmanager

import uvicorn
from api.v1 import queues, websockets
from core.config import settings
from fastapi import FastAPI
from faststream.rabbit import RabbitBroker
from integration import rabbitmq, redis
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,  # decode binary to str
    )
    rabbitmq.rabbitmq_broker = RabbitBroker(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        login=settings.rabbitmq_login,
        password=settings.rabbitmq_password,
    )
    await rabbitmq.rabbitmq_broker.connect()
    await rabbitmq.configure_rabbit_queues()
    await rabbitmq.configure_rabbit_exchange()
    yield
    await redis.redis_client.close()
    await rabbitmq.rabbitmq_broker.close()


app = FastAPI(
    description="Сервис поиска людей для совместного просмотра фильма",
    version="0.0.0",
    title=settings.project_name,
    docs_url="/queue/api/openapi",
    openapi_url="/queue/api/openapi.json",
    lifespan=lifespan,
)

app.include_router(
    queues.router, prefix="/queues/api/v1", tags=["films_queues"]
)
app.include_router(
    websockets.router, prefix="/waiting_party/api/v1", tags=["waiting_party"]
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
