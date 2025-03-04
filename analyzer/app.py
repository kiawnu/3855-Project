import logging.config
import connexion
import logging
import yaml
import json
from pykafka import KafkaClient

# Open conf file
with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

# Open log config
with open("log_conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

# Define static variables
HOST = app_config["kafka"]["hostname"]
PORT = app_config["kafka"]["port"]
TOPIC = app_config["kafka"]["topic"]
INTERVAL = app_config["scheduler"]["interval"]

# Kafka

# Start logger
logger = logging.getLogger("basicLogger")
logger.info("Analyzer service started")


def get_ship_event(index):
    client = KafkaClient(hosts=f"{HOST}:{PORT}")
    topic = client.topics[str.encode(f"{TOPIC}")]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    counter = 0
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        payload = data["payload"]

        if data["type"] == "ship_arrival":
            if counter == index:
                logger.info(f"ship event found at index {counter}")
                return payload, 200
            counter += 1

    return {"message": f"No message at index {index}!"}, 404


def get_container_event(index):
    client = KafkaClient(hosts=f"{HOST}:{PORT}")
    topic = client.topics[str.encode(f"{TOPIC}")]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    counter = 0
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        payload = data["payload"]

        if data["type"] == "container_processing":
            if counter == index:
                logger.info(f"Container event found at index {counter}")
                return payload, 200
            counter += 1

    return {"message": f"No message at index {index}!"}, 404


# Get stats endpoint function
def get_stats():
    client = KafkaClient(hosts=f"{HOST}:{PORT}")
    topic = client.topics[str.encode(f"{TOPIC}")]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    ship_counter = 0
    container_counter = 0
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        if data["type"] == "ship_arrival":
            ship_counter += 1
        if data["type"] == "container_processing":
            container_counter += 1

    stats = {"num_ship_events": ship_counter, "num_container_events": container_counter}
    logger.info(f"Returning stats {stats} ")

    return stats, 200


app = connexion.FlaskApp(__name__, specification_dir="")

app.add_api(
    "KABDOLLAHI1-ShippingAPI-1.0.0.0-resolved.yaml",
    strict_validation=True,
    validate_responses=True,
)

if __name__ == "__main__":
    app.run(port=8200)
