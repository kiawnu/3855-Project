import logging.config
import connexion
import json
import logging
import yaml
import httpx
import time
from datetime import datetime, timedelta
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from flask import jsonify

# Open conf file
with open("/app/config/app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())


# Open log config
with open("/app/config/log_conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

STATS_FILE_PATH = app_config["datafile"]["path"]
STATS_FILE = app_config["datafile"]["file"]

prcessing_stats = app_config["endpoints"]["processing_stats"]["url"]
analyzer_ship_ids = app_config["endpoints"]["analyzer_stats"]["ship_url"]
analyzer_container_ids = app_config["endpoints"]["analyzer_stats"]["container_url"]

storage_ship_ids = app_config["endpoints"]["storage_stats"]["ship_url"]
storage_container_ids = app_config["endpoints"]["storage_stats"]["container_url"]


def run_consistency_checks():
    logger.info("Update process has started...")

    start = time.time()

    processing_event_counts_r = httpx.get(prcessing_stats)

    processing_event_counts = processing_event_counts_r.json()

    analyzer_ship_event_ids_r = httpx.get(analyzer_ship_ids)

    analyzer_ship_event_ids = analyzer_ship_event_ids_r.json()

    analyzer_container_event_ids_r = httpx.get(analyzer_container_ids)

    analyzer_container_event_ids = analyzer_container_event_ids_r.json()

    storage_ship_event_ids_r = httpx.get(storage_ship_ids)

    storage_ship_event_ids = storage_ship_event_ids_r.json()

    storage_container_event_ids_r = httpx.get(storage_container_ids)

    storage_container_event_ids = storage_container_event_ids_r.json()

    ship_analyzer_count = len(analyzer_ship_event_ids)
    ship_storage_count = len(storage_ship_event_ids)
    container_analyzer_count = len(analyzer_container_event_ids)
    container_storage_count = len(storage_container_event_ids)

    trace_ids_ship_queue = {event["trace_id"] for event in analyzer_ship_event_ids_r}

    trace_ids_ship_db = {event["trace_id"] for event in storage_ship_event_ids_r}

    trace_ids_container_queue = {
        event["trace_id"] for event in analyzer_container_event_ids_r
    }
    trace_ids_container_db = {
        event["trace_id"] for event in storage_container_event_ids_r
    }

    missing_ship_in_db = trace_ids_ship_queue - trace_ids_ship_db
    missing_ship_in_queue = trace_ids_ship_db - trace_ids_ship_queue

    missing_container_in_db = trace_ids_container_queue - trace_ids_container_db
    missing_container_in_queue = trace_ids_container_db - trace_ids_container_queue

    missing_ship_events_in_db = [
        event for event in trace_ids_ship_db if event["trace_id"] in missing_ship_in_db
    ]

    missing_ship_events_in_queue = [
        event
        for event in trace_ids_ship_queue
        if event["trace_id"] in missing_ship_in_queue
    ]

    missing_container_events_in_db = [
        event
        for event in trace_ids_container_db
        if event["trace_id"] in missing_container_in_db
    ]

    missing_container_events_in_queue = [
        event
        for event in trace_ids_container_queue
        if event["trace_id"] in missing_container_in_queue
    ]

    end = time.time()
    processing_time_ms = start - end

    current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    logger.info(
        f"Consistency checks completed, processing time: {processing_time_ms}, missing_ship_events_in_db: {missing_ship_events_in_db}, missing_ship_events_in_queue: {missing_ship_events_in_queue}, missing_container_events_in_db: {missing_container_events_in_db}, missing_container_events_in_queue: {missing_container_events_in_queue} "
    )

    stats_json = {
        "last_updated": current_time,
        "counts": {
            "db": {
                "ship_event": ship_storage_count,
                "container_event": container_storage_count,
            },
            "queue": {
                "ship_event": ship_analyzer_count,
                "container_event": container_analyzer_count,
            },
            "processing": {
                "ship_event": processing_event_counts["num_ships_arrived"],
                "container_event": processing_event_counts["num_containers_proccessed"],
            },
        },
        "missing_ship_in_db": missing_ship_events_in_db,
        "missing_container_in_db": missing_container_events_in_db,
        "missing_ship_in_queue": missing_ship_events_in_queue,
        "missing_container_in_queue": missing_container_events_in_queue,
    }

    if not STATS_FILE_PATH.is_file():
        logger.error("Stats file does not exist..creating")

        with open(STATS_FILE_PATH, "w") as f:
            f.write(json.dumps({}))
    else:
        with open(STATS_FILE_PATH, "w") as f:
            json.dump(stats_json)

    return {"processing_time_ms": processing_time_ms}


def get_checks():
    if not STATS_FILE_PATH.is_file():
        logger.error("Stats file does not exist")
        return 404

    else:
        with open(STATS_FILE_PATH, "r") as f:
            data = json.load(f)

        return jsonify(data), 200


logger = logging.getLogger("basicLogger")

app = connexion.FlaskApp(__name__, specification_dir="")

app.add_api(
    "consistency_check.yaml",
    strict_validation=True,
    validate_responses=True,
)

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    app.run(port=8400, host="0.0.0.0")
