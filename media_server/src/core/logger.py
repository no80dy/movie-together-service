import structlog

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processors": [
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(colors=False),
            ],
        },
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processors": [
                structlog.processors.JSONRenderer(),
            ],
        },
    },
    "handlers": {
        "console_handler": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console_formatter",
        },
        "json_handler": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/notifications/app.json",
            "formatter": "json_formatter",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console_handler", "json_handler"],
            "level": "DEBUG",
        },
        "uvicorn.error": {"level": "ERROR"},
        "uvicorn.access": {"handlers": ["console_handler"], "level": "DEBUG"},
    },
}
