import logging.config
import connexion
import uuid
import json
import yaml
import logging
import datetime
from connexion import NoContent
from pykafka import KafkaClient

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger("basicLogger")

# Kafka set up
HOST = app_config["events"]["hostname"]
PORT = app_config["events"]["port"]
TOPIC = app_config["events"]["topic"]

client = KafkaClient(hosts=f"{HOST}:{PORT}")
topic = client.topics[str.encode(f"{TOPIC}")]
producer = topic.get_sync_producer()


def report_ship_arrived(body):
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id

    logger.info(f"Received event report_ship_arrived with trace id {trace_id}")

    msg = {
        "type": "ship_arrival",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "payload": body,
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    logger.info(
        f"Response for event report_ship_arrived (id:{body['ship_id']}) has status {201}"
    )

    return NoContent, 201


def report_container_processed(body):
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id

    logger.info(f"Received event report_container_processed with trace id {trace_id}")

    msg = {
        "type": "container_processing",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "payload": body,
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    logger.info(
        f"Response for event report_container_processed (id:{body['container_id']}) has status {201}"
    )

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir="")

app.add_api(
    "KABDOLLAHI1-ShippingAPI-1.0.0.0-resolved.yaml",
    strict_validation=True,
    validate_responses=True,
)

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
