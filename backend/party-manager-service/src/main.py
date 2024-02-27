import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from integration import mongodb, rabbitmq
from faststream.rabbit import RabbitBroker


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb.mongo_client = AsyncIOMotorClient(settings.mongodb_url)
    rabbitmq.rabbitmq_broker = RabbitBroker(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        login=settings.rabbitmq_login,
        password=settings.rabbitmq_password
    )
    await rabbitmq.rabbitmq_broker.connect()
    await rabbitmq.configure_rabbit_queues()
    await rabbitmq.configure_rabbit_exchange()
    yield
    await rabbitmq.rabbitmq_broker.close()
    mongodb.mongo_client.close()


app = FastAPI(
    description="Party Manager Service",
    version="0.0.0",
    title=settings.project_name,
    docs_url="/party-manager-service/api/openapi",
    openapi_url="/party-manager-service/api/openapi.json",
    lifespan=lifespan
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
