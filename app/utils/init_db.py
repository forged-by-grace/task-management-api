from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.configuration import AppConfig
from app.utils.config_helper import get_config

# Load app configuration
cfg = get_config()

# Init the SQLite database url
SQLALCHEMY_DATABASE_URL = cfg.app.db_url
    
# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a local session class instance
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# set the base class to be inherited by SQLALCHEMY models
Base = declarative_base()