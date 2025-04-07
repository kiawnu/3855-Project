import logging.config
import connexion
import json
import logging
import yaml
import httpx
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

prcessing_stats = app_config["endpoints"]["processing_stats"]["url"]
analyzer_ship_ids = app_config["endpoints"]["analyzer_stats"]["ship_url"]
analyzer_container_ids = app_config["endpoints"]["analyzer_stats"]["container_url"]

storage_ship_ids = app_config["endpoints"]["storage_stats"]["ship_url"]
storage_container_ids = app_config["endpoints"]["storage_stats"]["container_url"]


def run_consistency_checks():
    processing_event_counts = httpx.get(prcessing_stats)

    analyzer_ship_event_ids = httpx.get(analyzer_ship_ids)
    analyzer_container_event_ids = httpx.get(analyzer_container_ids)

    storage_ship_event_ids = httpx.get(storage_ship_ids)
    storage_container_event_ids = httpx.get(storage_container_ids)

    return (
        processing_event_counts,
        analyzer_container_event_ids,
        analyzer_ship_event_ids,
        storage_container_event_ids,
        storage_ship_event_ids,
    )


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
