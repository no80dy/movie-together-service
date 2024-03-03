from faststream.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitExchange,
    RabbitQueue,
)

rabbitmq_broker: RabbitBroker | None = None


async def configure_rabbit_exchange():
    await rabbitmq_broker.declare_exchange(
        RabbitExchange(name="party-manager-service", type=ExchangeType.FANOUT)
    )


async def configure_rabbit_queues():
    await rabbitmq_broker.declare_queue(
        RabbitQueue(name="party-manager-service.party_creation")
    )


def get_rabbitmq() -> RabbitBroker:
    return rabbitmq_broker
