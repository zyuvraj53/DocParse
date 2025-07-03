import re
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, configure_mappers
from sqlalchemy.dialects.postgresql.base import PGDialect

# Patch SQLAlchemy for CockroachDB version parsing
def _get_server_version_info(self, connection):
    version_string = connection.exec_driver_sql("SELECT version()").scalar()
    match = re.match(r"CockroachDB.*v(\d+)\.(\d+)\.(\d+)", version_string)
    if match:
        return tuple(int(x) for x in match.groups())
    return (20, 0, 0)

PGDialect._get_server_version_info = _get_server_version_info

DATABASE_URL = "postgresql://root@localhost:26257/resume_db?sslmode=disable"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import models to ensure they are registered with SQLAlchemy
from models import models  # Adjust the import path if necessary

# Configure mappers to resolve relationships
configure_mappers()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()