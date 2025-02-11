import logging.config
import connexion, json, datetime, logging, yaml
from datetime import datetime
from connexion import NoContent
from pathlib import Path
from db import make_session, create_tables, drop_tables
from models import ShipArrivals, ContainerProcessing
from sqlalchemy import select



with open("log_conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger('basicLogger')


def report_ship_arrived(body):
    session = make_session()

    event = ShipArrivals(**body)

    event.docking_time = datetime.strptime(event.docking_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    trace_id = event.trace_id

    session.add(event)
    session.commit()
    session.close()

    logger.debug(f"Stored event report_ship_arrived with trace id of {trace_id}")

    return NoContent, 201

def report_container_processed(body):
    session = make_session()

    event = ContainerProcessing(**body)
    
    event.unloading_time = datetime.strptime(event.unloading_time, "%Y-%m-%dT%H:%M:%S.%fZ")

    trace_id = event.trace_id


    session.add(event)
    session.commit()
    session.close()

    logger.debug(f"Stored event report_container_processed with trace id of {trace_id}")



    return NoContent, 201

def get_ship_event(start_timestamp, end_timestamp):

    session = make_session()

    start = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    statement = select(ShipArrivals).where(ShipArrivals.date_created >= start).where(ShipArrivals.date_created < end)

    results = [
        result.to_dict()
        for result in session.execute(statement).scalars().all()
    ]
    session.close()

    logger.info("Found %d ship arrival events (start: %s, end: %s)", len(results), start, end)   
    return results

def get_container_event(start_timestamp, end_timestamp):

    session = make_session()

    start = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    statement = select(ContainerProcessing).where(ContainerProcessing.date_created >= start).where(ContainerProcessing.date_created < end)

    results = [
        result.to_dict()
        for result in session.execute(statement).scalars().all()
    ]
    session.close()

    logger.info("Found %d ship arrival events (start: %s, end: %s)", len(results), start, end)   
    return results

app = connexion.FlaskApp(__name__, specification_dir='')

app.add_api("KABDOLLAHI1-ShippingAPI-1.0.0.0-resolved.yaml", 
    strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090)
