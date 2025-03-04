import logging.config
import connexion
import json
import logging
import yaml
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from flask import jsonify

# Open conf file
with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

# Define static variables

STATS_FILE = app_config["datastore"]["filename"]
STATS_FILE_PATH = Path(STATS_FILE)
INTERVAL = app_config["scheduler"]["interval"]
SHIP_ENDPOINT = app_config["eventstores"]["ship_arrivals"]["url"]
CONTAINER_ENDPOINT = app_config["eventstores"]["container_processing"]["url"]

# Open log config
with open("log_conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger("basicLogger")


# Get stats endpoint function
def get_stats():
    logger.info("Stat request received")

    if STATS_FILE_PATH.is_file():
        with open(STATS_FILE, "r") as f:
            data = json.load(f)
        logger.debug(data)
        logger.info("Stats request completed")
        return jsonify(data), 200

    else:
        logger.error("Stats file does not exist.")
        return {"error": "Stats file does not exist"}, 404


# Gather and populate stats file
def populate_stats():
    logger.info("Periodic processing has started")

    current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    # time.sleep(5)

    # If no JSON file present, will use the default value to get all events
    default_values = {"last_updated": "1970-02-10T12:34:56Z"}

    if STATS_FILE_PATH.is_file():
        with open(STATS_FILE, "r") as f:
            stats_json = json.load(f)

    else:
        logger.info("Stats file does not exist. Using default values.")
        stats_json = {
            "num_ships_arrived": 0,
            "num_containers_proccessed": 0,
            "max_containers_onboard": 0,
            "heaviest_container": 0,
            "lightest_container": 10000000,
            "last_updated": default_values["last_updated"],
        }

    start = stats_json["last_updated"]

    params = {
        "start_timestamp": start,
        "end_timestamp": current_time,
    }

    # API responses
    ship_events_r = httpx.get(SHIP_ENDPOINT, params=params)
    container_events_r = httpx.get(CONTAINER_ENDPOINT, params=params)

    # json objects
    ship_events = ship_events_r.json()
    container_events = container_events_r.json()

    # Error handlingen
    if container_events_r.status_code != 200:
        logger.error(
            f"Error fetching container events, Response: {container_events_r.status_code}"
        )
    if ship_events_r.status_code != 200:
        logger.error(
            f"Error fetching ship events, Response: {ship_events_r.status_code}"
        )

    logger.info(
        f"Number of ship events: {len(ship_events)}, Number of container events: {len(container_events)}"
    )

    # Stat calculations

    if len(container_events) > 0:
        current_max_weight = stats_json["heaviest_container"]
        current_min_weight = stats_json["lightest_container"]

        stats_json["num_containers_proccessed"] += len(container_events)

        temp_heavy = max(container_events, key=lambda x: x["container_weight"])[
            "container_weight"
        ]

        temp_lightest = min(container_events, key=lambda x: x["container_weight"])[
            "container_weight"
        ]

        if current_max_weight < temp_heavy:
            stats_json["heaviest_container"] = temp_heavy

        if current_min_weight > temp_lightest:
            stats_json["lightest_container"] = temp_lightest

        last_container_event = datetime.strptime(
            container_events[-1]["date_created"], "%Y-%m-%dT%H:%M:%SZ"
        )

    if len(ship_events) > 0:
        current_max_containers = stats_json["max_containers_onboard"]

        stats_json["num_ships_arrived"] += len(ship_events)

        temp_max = max(ship_events, key=lambda x: x["containers_onboard"])[
            "containers_onboard"
        ]

        if current_max_containers < temp_max:
            stats_json["max_containers_onboard"] = temp_max

        last_ship_event = datetime.strptime(
            ship_events[-1]["date_created"], "%Y-%m-%dT%H:%M:%SZ"
        )

        # Get the most recent timestamp

    # if len(ship_events) > 0 and len(container_events) > 0:
    #     # most_recent = max(last_ship_event, last_container_event)
    #     most_recent = max(last_container_event, last_ship_event)

    #     # Convert back to proper format
    #     date_formatted = most_recent.strftime("%Y-%m-%dT%H:%M:%SZ")
    #     logger.debug(date_formatted)
    #     stats_json["last_updated"] = date_formatted

    # else:
    #     stats_json["last_updated"] = current_time
    stats_json["last_updated"] = current_time

    with open(STATS_FILE, "w") as f:
        json.dump(stats_json, f, indent=4)

    logger.debug(f"New stat values: {stats_json}")
    logger.info("Period processing has ended")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, "interval", seconds=INTERVAL)
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir="")

app.add_api(
    "KABDOLLAHI1-ShippingAPI-1.0.0.0-resolved.yaml",
    strict_validation=True,
    validate_responses=True,
)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, host="0.0.0.0")
