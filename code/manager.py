import threading
from typing import Dict
from datetime import datetime, timedelta
from time import sleep
from sqlalchemy import sql, Engine
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import hashlib


class DeleteManager:
    def __init__(self, engine: Engine):
        """
        Data structure for adding, tracking and deleting secrets
        :param engine: sqlalchemy.Engine
            Engine to use for connecting to database objects
        """
        self.event = threading.Event()
        self.thread = threading.Thread(target=self._next_target, args=(engine,))
        self.thread.start()
        self.is_empty = True

    def add(self, secret: str, phrase: str, cipher: Fernet, engine: Engine, delete_date: None) -> str:
        """
        Adding new secret to database
        :param secret: secret's text
        :param phrase: code phrase to unlock a secret
        :param cipher: cryptography.fernet.Fernet
        :param engine: sqlalchemy.Engine
            Engine to use for connecting to database objects
        :param delete_date: interval after which unlocked secret will be delete
            may be None (secret will store unlimited time)
            or between 1 second ana 6 days 23 hours 59 minutes 59 seconds
        :return: unique secret key of stored message
        """
        if self.is_empty:
            self.event.set()
            self.is_empty = False
        with engine.begin() as conn:
            query = sql.text("SELECT Secret.generate_secret(:phrase, :secret, :delete_date)")
            result = conn \
                .execute(query,
                         phrase=generate_password_hash(phrase),
                         secret=cipher.encrypt(str.encode(secret)),
                         delete_date=delete_date) \
                .fetchone()[0]
            secret_key = hashlib.sha256(str.encode(str(result))).hexdigest()
            upd = sql.text("UPDATE Secret.Storage SET SecretKey = :skey WHERE StorageId = :id")
            conn.execute(upd, skey=secret_key, id=result)
        return secret_key

    def _next_target(self, engine: Engine) -> None:
        """
        Определить следующее время удаления секрета, как
        """
        sleep(0.01)
        query = sql.text("SELECT MIN(DeleteDate) - CURRENT_TIMESTAMP FROM Secret.Storage")
        while True:
            wait_time = engine.execute(query).fetchone()[0]
            if wait_time is None:
                break
            wait_time = wait_time.microseconds / 100000
            self.event.clear()
            self.event.wait(wait_time)
            self._delete(engine)

        self.is_empty = True
        self.event.clear()
        self.event.wait(10)
        self._next_target(engine)

    @staticmethod
    def _delete(engine: Engine) -> None:
        with engine.begin() as conn:
            query = sql.text("DELETE FROM Secret.Storage WHERE DeleteDate <= CURRENT_TIMESTAMP")
            conn.execute(query)
