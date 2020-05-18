class Config:
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    # SECRET_KEY = Fernet.generate_key()
    SECRET_KEY = 'FufYG5xG9ao1HWT4J7AKbFVL_P8sWyRRItG-VVgY-TQ='
    DEBUG = False
    POSTGRES_USER = 'secret_user'
    POSTGRES_PASSWORD = 'secret'
    POSTGRES_DB = 'secret_db'
    DATABASE_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"