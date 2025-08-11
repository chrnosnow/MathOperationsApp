import json
import asyncio
from aiokafka import AIOKafkaConsumer

message_store = []  # Store messages in memory for FastAPI access


async def consume_kafka():
    print(" Starting Kafka consumer...")

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
            print(" Kafka consumer is running")

            async for message in consumer:
                print(f" Consumed message from [{message.topic}]: {message.value}")

                # Append message to shared store
                message_store.append({
                    "topic": message.topic,
                    "message": message.value
                })

        except Exception as e:
            print(f" Error in Kafka consumer loop: {e}")
            await asyncio.sleep(2)  # Wait before retrying

        finally:
            await consumer.stop()
            print(" Kafka consumer stopped (will retry if looped)")
