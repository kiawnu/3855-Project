import logging.config
import connexion
import json
import logging
import yaml
import os
from datetime import datetime
from pykafka import KafkaClient
from pathlib import Path
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from flask import jsonify
from dotenv import load_dotenv

dotenv_path = Path("../.env")
load_dotenv(dotenv_path=dotenv_path)

CONTAINER_WEIGHT_MAX = os.getenv("CONTAINER_WEIGHT_MAX")
CONTAINER_ONB_MAX = os.getenv("CONTAINER_ONB_MAX")


# Open conf file
with open("/app/config/app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())


# Open log config
with open("/app/config/log_conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

STATS_FILE_PATH = app_config["datafile"]["path"]
STATS_FILE = app_config["datafile"]["file"]
stats_file_path = Path(STATS_FILE_PATH)

# KAFKA
HOST = app_config["kafka"]["hostname"]
PORT = app_config["kafka"]["port"]
TOPIC = app_config["kafka"]["topic"]


logger = logging.getLogger("basicLogger")

logger.info(
    f"Anomaly service started with CONTAINER_WEIGHT_MAX: {CONTAINER_WEIGHT_MAX} and CONTAINER_ONB_MAX: {CONTAINER_ONB_MAX}"
)


def update_anomalies():
    client = KafkaClient(hosts=f"{HOST}:{PORT}")
    topic = client.topics[str.encode(f"{TOPIC}")]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    anomalies = []
    logger.debug("update endpoint request received")

    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        payload = data["payload"]

        if data["type"] == "ship_arrival":
            if payload["containers_onboard"] > 10000:
                anomalies.append(
                    {
                        "event_id": payload["ship_id"],
                        "trace_id": payload["trace_id"],
                        "event_type": "ship_arrival",
                        "anomaly_type": "Too High",
                        "description": f"Too many conatainers aboard, detected {payload['containers_onboard']} containers",
                    }
                )
                logger.debug("Anomaly found for ship event")
        if data["type"] == "container_processing":
            if payload["container_weight"] > 1000:
                anomalies.append(
                    {
                        "event_id": payload["container_id"],
                        "trace_id": payload["trace_id"],
                        "event_type": "container_processing",
                        "anomaly_type": "Too High",
                        "description": f"Container weight too high, detected weight of: {payload['container_weight']}",
                    }
                )
                logger.debug("Anomaly found for container event")
    stats_json = {"anomalies": anomalies}

    if not stats_file_path.is_file():
        logger.error("Stats file does not exist..creating")

        with open(stats_file_path, "w") as f:
            f.write(json.dumps({}))

    with open(stats_file_path, "w") as f:
        json.dump(stats_json, f)

    return {"anomalies_count": len(anomalies)}


def get_anomalies(event_type=None):
    if event_type not in ["ship_arrival", "container_processing", None]:
        return {
            "message": " Invalid Event Type, must be container_processing or ship_arrival"
        }, 400

    # if event_type != "container_processing":
    #     return {
    #         "message": " Invalid Event Type, must be container_processing or ship_arrival"
    #     }, 400

    # if event_type is not None:
    #     return {
    #         "message": " Invalid Event Type, must be container_processing or ship_arrival"
    #     }, 400

    if not stats_file_path.is_file():
        logger.error("Stats file does not exist")
        return {"message": "The anomalies datastore is missing or corrupted"}, 404

    else:
        with open(stats_file_path, "r") as f:
            data = json.load(f)
            data = jsonify(data)

        if event_type == "None":
            return data, 200


app = connexion.FlaskApp(__name__, specification_dir="")

app.add_api(
    "anomaly.yaml",
    base_path="/anomaly_detector",
    strict_validation=True,
    validate_responses=True,
)

if "CORS_ALLOW_ALL" in os.environ and os.environ["CORS_ALLOW_ALL"] == "yes":
    app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if __name__ == "__main__":
    app.run(port=8500, host="0.0.0.0")
