import logging.config
import connexion
import logging
import yaml
import json
from threading import Thread
from pykafka import KafkaClient
from pykafka.common import OffsetType
from datetime import datetime
from db import make_session
from models import ShipArrivals, ContainerProcessing
from sqlalchemy import select

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

# Kafka set up
HOST = app_config["events"]["hostname"]
PORT = app_config["events"]["port"]
TOPIC = app_config["events"]["topic"]

logger = logging.getLogger("basicLogger")


def process_messages():
    """Process event messages"""

    hostname = f"{HOST}:{PORT}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(f"{TOPIC}")]

    consumer = topic.get_simple_consumer(
        consumer_group=b"event_group",
        reset_offset_on_start=False,
        auto_offset_reset=OffsetType.LATEST,
    )

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode("utf-8")
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]

        if msg["type"] == "ship_arrival":
            session = make_session()

            event = ShipArrivals(**payload)

            event.docking_time = datetime.strptime(
                event.docking_time, "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            trace_id = event.trace_id

            session.add(event)
            session.commit()
            session.close()
            logger.debug(
                f"Stored event report_ship_arrived with trace id of {trace_id}"
            )

        elif msg["type"] == "container_processing":
            session = make_session()

            event = ContainerProcessing(**payload)

            event.unloading_time = datetime.strptime(
                event.unloading_time, "%Y-%m-%dT%H:%M:%S.%fZ"
            )

            trace_id = event.trace_id

            session.add(event)
            session.commit()
            session.close()

            logger.debug(
                f"Stored event report_container_processed with trace id of {trace_id}"
            )

        # Commit the new message as being read
        consumer.commit_offsets()


def get_ship_event(start_timestamp, end_timestamp):
    session = make_session()

    start = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    statement = (
        select(ShipArrivals)
        .where(ShipArrivals.date_created >= start)
        .where(ShipArrivals.date_created < end)
    )

    results = [
        result.to_dict() for result in session.execute(statement).scalars().all()
    ]
    session.close()

    logger.info(
        "Found %d ship arrival events (start: %s, end: %s)", len(results), start, end
    )
    return results


def get_container_event(start_timestamp, end_timestamp):
    session = make_session()

    start = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    statement = (
        select(ContainerProcessing)
        .where(ContainerProcessing.date_created >= start)
        .where(ContainerProcessing.date_created < end)
    )

    results = [
        result.to_dict() for result in session.execute(statement).scalars().all()
    ]
    session.close()

    logger.info(
        "Found %d ship arrival events (start: %s, end: %s)", len(results), start, end
    )
    return results


def setup_kafka_thread():
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()


app = connexion.FlaskApp(__name__, specification_dir="")

app.add_api(
    "KABDOLLAHI1-ShippingAPI-1.0.0.0-resolved.yaml",
    strict_validation=True,
    validate_responses=True,
)

if __name__ == "__main__":
    setup_kafka_thread()
    app.run(port=8090)
