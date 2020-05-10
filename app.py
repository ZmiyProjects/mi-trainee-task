from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, sql
from cryptography.fernet import Fernet
from collections import namedtuple
import hashlib
import threading
from typing import Dict
from datetime import datetime, timedelta
from time import sleep
from manager import DeleteManager

Keeper = namedtuple("Keeper", ['phrase', 'message'])

app = Flask(__name__)
app.config.from_object('config.PostgresConfig')
db = create_engine(app.config['DATABASE_URI'])
db_manager = DeleteManager(db)


@app.route('/generate', methods=['POST'])
def new_secret():
    values = request.get_json()
    secret = values.get("secret")
    delete_date = values.get("delete_date")
    if secret is None:
        return {}, 400
    phrase = values.get("phrase")
    if phrase is None:
        return {}, 400
    cipher = Fernet(app.config['SECRET_KEY'])
    db_manager.add(secret, phrase, delete_date, cipher)
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
        return jsonify(data="указанный ключ отсутствует!"), 400
    result = Keeper(*result)
    if check_password_hash(result.phrase, phrase):
        cipher = Fernet(app.config['SECRET_KEY'])
        with db.begin() as conn:
            conn.execute(sql.text("DELETE FROM Secret.Storage WHERE SecretKey = :id"), id=secret_key)
        return jsonify(data=cipher.decrypt(bytes(result.message)).decode("utf-8")), 200
    return {}, 403


if __name__ == '__main__':
    app.run(host='0.0.0.0')
