from contextlib import asynccontextmanager

import uvicorn
from api.v1 import groups, permissions, users
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from core.config import settings
from db import storage
from db.redis import RedisStorage
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from starlette.middleware.sessions import SessionMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.nosql_storage = RedisStorage(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True,
    )
    yield
    await storage.nosql_storage.close()


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name="jaeger",
                agent_port=6831,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )


configure_tracer()


app = FastAPI(
    description="Сервис по авторизации и аутентификации пользователей",
    version="1.0.0",
    title=settings.PROJECT_NAME,
    docs_url="/auth/api/openapi",
    openapi_url="/auth/api/openapi.json",
    default_response_class=JSONResponse,
    lifespan=lifespan,
)


FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )
    return response


app.include_router(users.router, prefix="/auth/api/v1/users", tags=["users"])
app.include_router(
    groups.router, prefix="/auth/api/v1/groups", tags=["groups"]
)
app.include_router(
    permissions.router, prefix="/auth/api/v1/permissions", tags=["permissios"]
)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    """Exception handler for authjwt."""
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.message}
    )


app.add_middleware(SessionMiddleware, secret_key="secret-string")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
