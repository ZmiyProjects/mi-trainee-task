from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, sql
from cryptography.fernet import Fernet
from collections import namedtuple
import hashlib
import threading
from typing import Dict
from datetime import datetime, timedelta
import os
import socket
from time import sleep
from manager import DeleteManager
from validators import interval_before_delete
import http.client

Keeper = namedtuple("Keeper", ['phrase', 'message'])

so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        so.connect(('db', 5432))
        so.close()
        break
    except socket.error:
        sleep(1)


app = Flask(__name__)
app.config.from_object('config.PostgresConfig')
db = create_engine(app.config['DATABASE_URI'])
db_manager = DeleteManager(db)
cipher = Fernet(app.config['SECRET_KEY'])


@app.route('/generate', methods=['POST'])
def new_secret():
    values = request.get_json()
    secret = values.get("secret")
    if secret is None:
        return jsonify(err_message='Секрет не задан!'), 400
    phrase = values.get("phrase")
    if phrase is None:
        return jsonify(err_message='Не указана фразу-ключ!'), 400
    before_delete = values.get("before_delete")
    try:
        if before_delete is not None:
            days = before_delete.get('days', 0)
            hours = before_delete.get('hours', 0)
            minutes = before_delete.get('minutes', 0)
            seconds = before_delete.get('seconds', 0)
            before_delete = interval_before_delete(days, hours, minutes, seconds)
    except ValueError:
        return jsonify(err_message='Некорректная дата удаления!'), 400
    secret_key = db_manager.add(secret, phrase, cipher, db, before_delete)
    return jsonify(data=secret_key), 201


@app.route('/secrets/<secret_key>', methods=['GET'])
def get_secret(secret_key):
    values = request.get_json()
    phrase = values.get("phrase")
    if phrase is None:
        return {}, 400
    query = sql.text("SELECT phrase, SecretMessage FROM Secret.Storage WHERE SecretKey = :id")
    result = db.execute(query, id=secret_key).fetchone()
    if result is None:
        return jsonify(err_message="указанный ключ отсутствует!"), 400
    result = Keeper(*result)
    if check_password_hash(result.phrase, phrase):
        with db.begin() as conn:
            conn.execute(sql.text("DELETE FROM Secret.Storage WHERE SecretKey = :id"), id=secret_key)
        return jsonify(data=cipher.decrypt(bytes(result.message)).decode("utf-8")), 200
    return jsonify(err_message='неверная кодовая фраза!'), 403


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
