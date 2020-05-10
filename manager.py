import threading
from typing import Dict
from datetime import datetime, timedelta
from time import sleep
from sqlalchemy import sql


class DeleteManager:
    def __init__(self, engine):
        self.event = threading.Event()
        self.thread = threading.Thread(target=self._next_target, args=(engine,))
        self.thread.start()
        self.is_empty = True

    def add(self, secret, phrase, delete_date, cipher):
        if self.is_empty:
            self.event.set()
            self.is_empty = False
        with db.begin() as conn:
            query = sql.text("SELECT Secret.generate_secret(:phrase, :secret, :delete_date)")
            result = conn \
                .execute(query, phrase=generate_password_hash(
                    phrase), secret=cipher.encrypt(str.encode(secret)), delete_date=delete_date) \
                .fetchone()[0]
            secret_key = hashlib.sha256(str.encode(str(result))).hexdigest()
            upd = sql.text("UPDATE Secret.Storage SET SecretKey = :skey WHERE StorageId = :id")
            conn.execute(upd, skey=secret_key, id=result)

    def _next_target(self, engine):
        sleep(0.01)
        query = sql.text("SELECT MIN(DeleteDate) - CURRENT_TIMESTAMP FROM Secret.Storage")
        while True:
            wait_time = engine.execute(query).fetchone()[0]
            if wait_time is None:
                break
            self.event.clear()
            self.event.wait(wait_time)
            self._delete(engine)

        self.is_empty = True
        self.event.clear()
        self.event.wait()
        self._next_target(engine)

    @static_method
    def _delete(engine):
        with engine.begin() as conn:
            query = sql.text("DELETE FROM Secret.Storage WHERE DeleteDate <= CURRENT_TIMESTAMP")
            conn.exicute(query)
