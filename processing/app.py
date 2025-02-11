import logging.config
import connexion, json, datetime, logging, yaml, httpx
from datetime import datetime
from connexion import NoContent
from pathlib import Path
from sqlalchemy import select
from apscheduler.schedulers.background import BackgroundScheduler
from flask import jsonify

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

STATS_FILE = app_config["datastore"]["filename"]
STATS_FILE_PATH = Path(STATS_FILE)
INTERVAL = app_config["scheduler"]["interval"]
SHIP_ENDPOINT = app_config["eventstores"]["ship_arrivals"]["url"]
CONTAINER_ENDPOINT = app_config["eventstores"]["container_processing"]["url"]

with open("log_conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger('basicLogger')

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
        return {"error": "Stats file does not exist"},404

        
def populate_stats():
    logger.info("Periodic processing has started")
    
    current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    default_values = {
            "last_updated": "1970-02-10T12:34:56.789Z" 
            }


    if STATS_FILE_PATH.is_file():
        with open(STATS_FILE, "r") as f:
            data = json.load(f)
        most_recent_event_time = data[0]["last_updated"]

    else:
        logger.info("Stats file does not exist. Using default values.")
        data = []
        most_recent_event_time = default_values["last_updated"]
        
        
    params = {
        "start_timestamp": most_recent_event_time,
        "end_timestamp": current_time,
    }
        
    ship_events_r = httpx.get(SHIP_ENDPOINT, params=params )
    container_events_r = httpx.get(CONTAINER_ENDPOINT, params=params)

    # json objects
    ship_events = ship_events_r.json()
    container_events = container_events_r.json()
    print(len(ship_events))

    if container_events_r.status_code != 200:
        logger.error(f"Error fetching container events, Response: {container_events_r.status_code}")
    if ship_events_r.status_code != 200:
        logger.error(f"Error fetching ship events, Response: {ship_events_r.status_code}")

    logger.info(f"Number of ship events: {len(ship_events)}, Number of container events: {len(container_events)}")
    
    # Stat calculations
    num_ships_arrived = len(ship_events)
    num_containers_processed = len(container_events)
    max_containers_onboard = max(ship_events, key=lambda x: x["containers_onboard"])
    heaviest_container = max(container_events, key=lambda x: x["container_weight"])
    lightest_container = min(container_events, key=lambda x: x["container_weight"])
    
    # Most recent event timestamp
    last_ship_event = datetime.strptime(ship_events[-1]["date_created"], "%Y-%m-%dT%H:%M:%SZ")
    last_container_event = datetime.strptime(container_events[-1]["date_created"], "%Y-%m-%dT%H:%M:%SZ")

    # Get the most recent timestamp
    most_recent = max(last_ship_event, last_container_event)

    # Convert back to proper format
    date_formatted = most_recent.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z"


    stats_json = [{
            "num_ships_arrived": num_ships_arrived,
            "num_containers_proccessed": num_containers_processed,
            "max_containers_onboard": max_containers_onboard["containers_onboard"],
            "heaviest_container": heaviest_container["container_weight"],
            "lightest_container": lightest_container["container_weight"],
            "last_updated": date_formatted 
            }]

    # write to json
    with open(STATS_FILE, "w") as f:
        json.dump(stats_json, f, indent=4)

    logger.debug(f"New stat values: {stats_json}")
    logger.info("Period processing has ended")

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,'interval',seconds=INTERVAL)
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')

app.add_api("KABDOLLAHI1-ShippingAPI-1.0.0.0-resolved.yaml", 
    strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
