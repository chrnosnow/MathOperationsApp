import json
from kafka import KafkaConsumer

message_store = []  # Store messages in memory for FastAPI access


def consume_kafka():
    try:
        consumer = KafkaConsumer(
            'fibonacci-requests',
            'pow-requests',
            'factorial-requests',
            bootstrap_servers='kafka:9092',
            group_id='fastapi-consumer',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )

        for message in consumer:
            try:
                print(f" Consumed from [{message.topic}]: {message.value}")
                message_store.append({
                    "topic": message.topic,
                    "message": message.value
                })
            except Exception as e:
                print(f" Error processing message from {message.topic}: {e}")

    except Exception as e:
        print(f" Kafka consumer failed to start: {e}")