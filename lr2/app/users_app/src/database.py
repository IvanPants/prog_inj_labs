from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import get_config

settings = get_config()
print(f'Using PostgreSQL connection string2: {settings.postgres_str}')
engine = create_engine(settings.postgres_str, connect_args={'connect_timeout': settings.postgres_connection_timeout})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
