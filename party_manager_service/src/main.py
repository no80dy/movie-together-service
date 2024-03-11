from contextlib import asynccontextmanager

import redis.asyncio as aioredis
import uvicorn
from api.v1 import film, stream, websockets, broker
from core.config import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from faststream.rabbit import RabbitBroker
from integration import mongodb, rabbitmq, redis
from motor.motor_asyncio import AsyncIOMotorClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb.mongo_client = AsyncIOMotorClient(settings.mongodb_url)
    rabbitmq.rabbitmq_broker = RabbitBroker(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        login=settings.rabbitmq_login,
        password=settings.rabbitmq_password,
    )
    redis.redis_client = aioredis.Redis(
        host=settings.redis_host, port=settings.redis_port
    )
    await rabbitmq.rabbitmq_broker.connect()
    await rabbitmq.configure_rabbit_queues()
    await rabbitmq.configure_rabbit_exchange()
    yield
    await redis.redis_client.close()
    await rabbitmq.rabbitmq_broker.close()
    mongodb.mongo_client.close()


app = FastAPI(
    description="Party Manager Service",
    version="0.0.0",
    title=settings.project_name,
    docs_url="/party-manager-service/api/openapi",
    openapi_url="/party-manager-service/api/openapi.json",
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(
    film.router,
    prefix="/party-manager-service/api/v1/broker",
    tags=["RabbitMQ"],
)
app.include_router(
    stream.router, prefix="/party-manager-service/api/v1/stream", tags=["HLS"]
)
app.include_router(
    websockets.router, prefix="/party-manager-service", tags=["WebSockets"]
)
app.include_router(
    broker.router,
    prefix="/party-manager-service/api/v1/broker"
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
