from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
import json, logging, os
from users.models import SensorData
from django.db import transaction

logger = logging.getLogger('server')
logger.propagate = False

BATCH_SIZE = 500  # adjust based on your DB capabilities

class Command(BaseCommand):
    help = "Consumes Kafka messages and stores sensor data"

    def add_arguments(self, parser):
        parser.add_argument('--topic', type=str, default='iot_bulk_data', help='Kafka topic name')

    def handle(self, *args, **options):
        topic= options['topic']
        logger.info(f"Starting consumer for topic: {topic}")
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers= os.getenv('BOOTSTRAP_SERVERS'), #'localhost:9092','localhost:9092',
            value_deserializer=self.safe_deserializer,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='sensor-group'
        )

        batch = []
        for message in consumer:
            data = message.value
            if not data:
                logger.warning("Skipped empty or malformed message.")
                continue
            print(f"Received: {data}")
            batch.append(SensorData(
                device_id=data["device_id"],
                temperature=data["temperature"],
                humidity=data["humidity"],
                timestamp=data["timestamp"]
            ))

            if len(batch) >= BATCH_SIZE:
                self.flush_batch(batch)

        # flush remaining
        if batch:
            self.flush_batch(batch)

    def flush_batch(self, batch):
        try:
            with transaction.atomic():
                SensorData.objects.bulk_create(batch)
            logger.info(f"Inserted batch of {len(batch)} records")
            batch.clear()
        except Exception as e:
            logger.error(f"Batch insert failed: {e}")

    def safe_deserializer(self, m):
        try:
            if not m:
                return None
            return json.loads(m.decode('utf-8'))
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON: {m}")
            return None
