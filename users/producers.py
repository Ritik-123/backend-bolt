from kafka import KafkaProducer
import json, logging, time, random, uuid


logger= logging.getLogger('server')
logger.propagate = False

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def produce_bulk_data(topic, count):
    for i in range(count):
        data = {
            "device_id": f"sensor_{i % 10}", # uuid.uuid4, 
            "timestamp": time.time(),
            "temperature": round(random.uniform(20.0, 40.0), 2),
            "humidity": round(random.uniform(30.0, 70.0), 2)
        }
        logger.info(f"Sending: {data}")
        producer.send(topic, value=data)
        time.sleep(0.01)  # slight delay to simulate real flow
    producer.flush()


# produce_bulk_data("iot_bulk_data", count=100000)


if __name__ == "__main__":
    produce_bulk_data("iot_bulk_data", count=100000)