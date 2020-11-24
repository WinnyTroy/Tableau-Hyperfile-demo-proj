import os
import urllib
import sqlalchemy
import databases
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

host_server = os.environ.get('host_server', 'localhost')
db_server_port = urllib.parse.quote_plus(str(os.environ.get('db_server_port', '5432')))
database_name = os.environ.get('database_name', 'fastapidemo')
db_username = urllib.parse.quote_plus(str(os.environ.get('db_username', 'fastapidemouser')))
db_password = urllib.parse.quote_plus(str(os.environ.get('db_password', 'fastapidemo')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))
DATABASE_URL = f'postgresql://{db_username}:{db_password}@{host_server}:{db_server_port}/{database_name}?sslmode={ssl_mode}'

engine = sqlalchemy.create_engine(
    DATABASE_URL, pool_size=3, max_overflow=0
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = sqlalchemy.MetaData()
Base.metadata.create_all(bind=engine)

notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("story", sqlalchemy.String),
    sqlalchemy.Column("display", sqlalchemy.Boolean),
)

# databases query builder
database = databases.Database(DATABASE_URL)
