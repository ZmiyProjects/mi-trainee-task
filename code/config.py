from urllib.parse import quote_plus
from cryptography.fernet import Fernet
import os


class Config:
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    # SECRET_KEY = Fernet.generate_key()
    SECRET_KEY = 'FufYG5xG9ao1HWT4J7AKbFVL_P8sWyRRItG-VVgY-TQ='
    DEBUG = False


class PostgresConfig(Config):
    POSTGRES_USER=os.environ['POSTGRES_USER']
    POSTGRES_PASSWORD=os.environ['POSTGRES_PASSWORD']
    POSTGRES_DB=os.environ['POSTGRES_DB']
    DATABASE_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"
