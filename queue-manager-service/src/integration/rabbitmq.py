from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from core.config import settings


rabbitmq_broker: RabbitBroker | None = None


async def configure_rabbit_exchange():
    await rabbitmq_broker.declare_exchange(
        RabbitExchange(name=settings.rabbitmq_exchange_name, type=ExchangeType.FANOUT)
    )


async def configure_rabbit_queues():
    await rabbitmq_broker.declare_queue(
        RabbitQueue(name=settings.rabbitmq_queue_name, durable=True))

    await rabbitmq_broker.declare_queue(
        RabbitQueue(name="websocket_queue", durable=True)
    )


def get_rabbitmq():
    return rabbitmq_broker