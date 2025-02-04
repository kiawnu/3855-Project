import logging.config
import connexion, json, datetime, logging, yaml
from datetime import datetime
from connexion import NoContent
from pathlib import Path
from storage.db import make_session, create_tables, drop_tables
from storage.models import ShipArrivals, ContainerProcessing
from sqlalchemy import select
from apscheduler.schedulers.background import BackgroundScheduler



with open("log_conf.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger('basicLogger')

def get_stats():
    pass

def populate_stats():
    print("In function populate stats!")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    # sched.add_job(populate_stats,
    #     'interval',
    #     seconds=app_config['scheduler']['interval'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')

app.add_api("KABDOLLAHI1-ShippingAPI-1.0.0.0-resolved.yaml", 
    strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
