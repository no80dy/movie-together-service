import structlog
import uvicorn
from api.v1 import stream
from core.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

app = FastAPI(
    title=settings.project_name,
    description="Медиа сервер для трансляции HLS-видеопотока",
    version="0.0.0",
    docs_url="/media-service/api/openapi",
    openapi_url="/media-service/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


app.include_router(
    stream.router,
    prefix="/media-service/api/v1/hls",
    tags=["HTTP Live Streaming"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
