from urllib.parse import quote_plus
from cryptography.fernet import Fernet


class Config:
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    # SECRET_KEY = Fernet.generate_key()
    SECRET_KEY = 'FufYG5xG9ao1HWT4J7AKbFVL_P8sWyRRItG-VVgY-TQ='
    DEBUG = True


class MSSQLConfig(Config):
    DATABASE_URI = "mssql+pyodbc:///?odbc_connect={}".format(quote_plus(
            'DRIVER={ODBC DRIVER 17 for SQL SERVER};SERVER=;DATABASE=Weather;UID=weather_user_login;PWD=WeatherUser1'))


class PostgresConfig(Config):
    DATABASE_URI = "postgresql+psycopg2://secret_user:pass@localhost:5432/secrets"