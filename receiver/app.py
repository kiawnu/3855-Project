import logging.config
import connexion, json, datetime, httpx, uuid, yaml, logging
from connexion import NoContent
from pathlib import Path

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger('basicLogger')

def report_ship_arrived(body):

    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id

    logger.info(f'Received event report_ship_arrived with trace id {trace_id}')
    
    r = httpx.post(app_config['events']['ship_arrivals']['url'], json=body)

    logger.info(f"Response for event report_ship_arrived (id:{body['ship_id']}) has status {r.status_code}")

    return NoContent, r.status_code

def report_container_processed(body):
    
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id

    logger.info(f'Received event report_container_processed with trace id {trace_id}')


    r = httpx.post(app_config['events']['container_processing']['url'], json=body)

    logger.info(f"Response for event report_container_processed (id:{body['container_id']}) has status {r.status_code}")


    return NoContent, r.status_code


app = connexion.FlaskApp(__name__, specification_dir='')

app.add_api("KABDOLLAHI1-ShippingAPI-1.0.0.0-resolved.yaml", 
    strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
