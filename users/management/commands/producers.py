from django.core.management.base import BaseCommand
from kafka import KafkaProducer
import json, logging, time, random, os

logger = logging.getLogger('server')
logger.propagate = False

class Command(BaseCommand):
    help = "Produce bulk sensor data to Kafka"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100000, help='Number of messages to send')
        parser.add_argument('--topic', type=str, default='iot_bulk_data', help='Kafka topic name')

    def handle(self, *args, **options):
        count = options['count']
        topic = options['topic']
        logger.info(f"Producing {count} messages to topic: {topic}")

        producer = KafkaProducer(
            bootstrap_servers= os.getenv('BOOTSTRAP_SERVERS'), #'localhost:9092'
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        for i in range(count):
            data = {
                "device_id": f"sensor_{i % 10}",
                "timestamp": time.time(),
                "temperature": round(random.uniform(20.0, 40.0), 2),
                "humidity": round(random.uniform(30.0, 70.0), 2)
            }
            logger.info(f"Sending: {data}")
            producer.send(topic, value=data)
            time.sleep(0.01)

        producer.flush()
        self.stdout.write(self.style.SUCCESS(f"Produced {count} messages to topic '{topic}'"))
