import json
import asyncio
import logging
from aiokafka import AIOKafkaConsumer

logger = logging.getLogger("kafka-consumer")
logger.setLevel(logging.INFO)

message_store = []  # Store messages in memory for FastAPI access


async def consume_kafka():
    logger.info("Starting Kafka consumer...")

    consumer = AIOKafkaConsumer(
        'fibonacci-requests',
        'pow-requests',
        'factorial-requests',
        bootstrap_servers='kafka:9092',
        group_id='fastapi-consumer',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )

    while True:
        try:
            await consumer.start()
            logger.info("Kafka consumer is running.")

            async for message in consumer:
                logger.info(f"Consumed message from [{message.topic}]: {message.value}")

                message_store.append({
                    "topic": message.topic,
                    "message": message.value
                })

        except Exception as e:
            logger.exception(f"Error in Kafka consumer loop: {e}")
            await asyncio.sleep(2)

        finally:
            await consumer.stop()
            logger.warning("Kafka consumer stopped (will retry if looped).")