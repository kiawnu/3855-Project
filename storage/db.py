from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, yaml
from models import Base

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

USER = app_config['datastore']['user']
PASSWORD = app_config['datastore']['password']
HOSTNAME = app_config['datastore']['hostname']
PORT = app_config['datastore']['port']
DB = app_config['datastore']['db']

engine = create_engine(f"mysql://{USER}:{PASSWORD}@{HOSTNAME}/{DB}")

def make_session():
    return sessionmaker(bind=engine)()

def create_tables():
    Base.metadata.create_all(engine)

def drop_tables():
    Base.metadata.drop_all(engine)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_tables()
        
    create_tables()