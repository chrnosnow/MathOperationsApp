from aiokafka import AIOKafkaProducer
import json

producer = None  # To be initialized on startup


async def init_kafka_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )
    await producer.start()
    print(" Kafka producer is ready")


async def stop_kafka_producer():
    if producer:
        await producer.stop()
        print(" Kafka producer stopped")


async def send_request_to_kafka(data: dict, topic: str):
    if not producer:
        raise RuntimeError("Producer hath not been initialized!")

    try:
        print(f" Sending to topic '{topic}': {data}")
        await producer.send_and_wait(topic, data)
        print(" Message delivered to Kafka")
    except Exception as e:
        print(f" Kafka send error: {e}")
