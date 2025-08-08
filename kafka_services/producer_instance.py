from aiokafka import AIOKafkaProducer
from typing import Optional

producer: Optional[AIOKafkaProducer] = None # Global async producer instance
