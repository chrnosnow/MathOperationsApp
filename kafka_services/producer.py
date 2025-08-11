import json
import logging
from aiokafka import AIOKafkaProducer

logger = logging.getLogger("kafka-producer")
logger.setLevel(logging.INFO)

producer = None  # To be initialized on startup


async def init_kafka_producer():
    global producer
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        )
        await producer.start()
        logger.info("Kafka producer is ready.")
    except Exception as e:
        logger.exception(f"Failed to start Kafka producer: {e}")


async def stop_kafka_producer():
    global producer
    if producer:
        try:
            await producer.stop()
            logger.info("Kafka producer stopped.")
        except Exception as e:
            logger.exception(f"Error while stopping Kafka producer: {e}")


async def send_request_to_kafka(data: dict, topic: str):
    if not producer:
        logger.error("Kafka producer hath not been initialized!")
        raise RuntimeError("Producer hath not been initialized!")

    try:
        logger.info(f"Sending to topic '{topic}': {data}")
        await producer.send_and_wait(topic, data)
        logger.info("Message delivered to Kafka.")
    except Exception as e:
        logger.exception(f"Kafka send error: {e}")