from contextlib import asynccontextmanager

import uvicorn
from api.v1 import queues, websockets
from core.config import settings
from fastapi import FastAPI, Request
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


@app.middleware("http")
async def create_auth_header(
        request: Request,
        call_next, ):
    '''
    Check if there are cookies set for authorization. If so, construct the
    Authorization header and modify the request (unless the header already
    exists!)
    '''
    if ("Authorization" not in request.headers
            and "access_token_cookie" in request.cookies
    ):
        access_token = request.cookies["access_token_cookie"]

        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                f"Bearer {access_token}".encode(),
            )
        )
    response = await call_next(request)
    return response


app.include_router(
    queues.router, prefix="/queues/api/v1", tags=["films_queues"]
)
app.include_router(
    websockets.router, prefix="/waiting_party/api/v1", tags=["waiting_party"]
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
