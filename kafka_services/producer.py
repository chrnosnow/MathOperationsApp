from kafka_services.producer_instance import producer
import logging

logger = logging.getLogger("uvicorn.error")

async def send_request_to_kafka(data: dict, topic: str = "math-requests"):
    if not producer:
        logger.warning(" Kafka producer is not initialized.")
        return

    try:
        await producer.send_and_wait(topic, data)
        logger.info(f" Sent Kafka message to '{topic}': {data}")
    except Exception as e:
        logger.error(f" Failed to send Kafka message to '{topic}': {e}")