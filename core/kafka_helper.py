import json
import logging
import os

from aiokafka import AIOKafkaProducer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "request-log")
log = logging.getLogger(__name__)

producer: AIOKafkaProducer | None = None


async def start_kafka():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    await producer.start()
    log.info("Kafka producer ready")


async def stop_kafka():
    if producer:
        await producer.stop()
        log.info("Kafka producer stopped")
