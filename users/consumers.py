from kafka import KafkaConsumer
import json, logging, os
from users.models import SensorData
from django.db import transaction

logger= logging.getLogger('server')
logger.propagate = False

consumer = KafkaConsumer(
    'iot_bulk_data',
    bootstrap_servers= os.getenv('BOOTSTRAP_SERVERS'), #'localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='sensor-group'
)

def consume_and_store():
    for message in consumer:
        data = message.value
        logger.info(f"Received: {data}")
        # Store in DB
        with transaction.atomic():
            SensorData.objects.create(
                device_id=data["device_id"],
                temperature=data["temperature"],
                humidity=data["humidity"],
                timestamp=data["timestamp"]
            )

if __name__ == "__main__":
    consume_and_store()


# batch = []
# BATCH_SIZE = 1000

# for message in consumer:
#     data = message.value
#     batch.append(SensorData(
#         device_id=data["device_id"],
#         temperature=data["temperature"],
#         humidity=data["humidity"],
#         timestamp=data["timestamp"]
#     ))
#     if len(batch) >= BATCH_SIZE:
#         with transaction.atomic():
#             SensorData.objects.bulk_create(batch)
#         batch.clear()