import requests
import pytest
from collections import namedtuple
from time import sleep
import json

RequestResult = namedtuple("RequestResult", ["status", "message"])

with open("test_config.json") as  reader:
    conf = json.load(reader)

server_url = f'http://{conf["host"]}:{conf["port"]}'


def simple_post(url: str, secret: str, phrase: str, **kwargs):
    """
    Сохранение нового сообщения в БД
    """
    struct = {
        "secret": secret,
        "phrase": phrase,
        "before_delete": kwargs
    }
    result = requests.post(url, json=struct)
    message = result.json().get("data")
    if message is None:
        message = result.json().get("err_message")
    return RequestResult(result.status_code, message)


def test_delete_by_timer():
    """
    Проверка удаления секрета по таймеру
    """
    result = simple_post(
        f'{server_url}/generate',
        "Невероятно важное сообщение!",
        "секретный код",
        seconds=3
    )
    assert result.status == 201
    sleep(10)
    deleted = requests.get(f'{server_url}/secrets/{result.message}', json={"phrase": "секретный код"})
    assert deleted.status_code == 400
    assert deleted.json()['err_message'] == "указанный ключ отсутствует!"


def test_incorrect_insert():
    """
    Попытка сохранения пустой структуры вместо секрета
    """
    struct = {}
    result = requests.post(f'{server_url}/generate', json=struct)
    assert result.status_code == 400


def test_simple_post():
    """
    Проверка сохранения и получения секрета
    """
    result = simple_post(
        f'{server_url}/generate',
        "Невероятно важное сообщение!",
        "секретный код",
        seconds=10
    )
    assert result.status == 201
    check = requests.get(f'{server_url}/secrets/{result.message}', json={"phrase": "секретный код"})
    assert check.status_code == 200
    assert check.json()["data"] == "Невероятно важное сообщение!"


def test_delete_date():
    """
    Попытка сохранения секрета с некорректной датой удаления
    """
    result = simple_post(
        f'{server_url}/generate',
        "Невероятно важное сообщение!",
        "секретный код",
        days=8,
        hours=25
    )
    assert result.status == 400
    assert result.message == "Некорректная дата удаления!"


def test_del_after_get():
    """
    Попытка доступа к удаленному секрету
    """
    result = simple_post(
        f'{server_url}/generate',
        "Some message",
        "my secret key",
        seconds=10
    )
    print(result.message)
    assert result.status == 201
    check = requests.get(f'{server_url}/secrets/{result.message}', json={"phrase": "my secret key"})
    assert check.status_code == 200
    assert check.json()["data"] == "Some message"
    after_delete = requests.get(f'{server_url}/secrets/{result.message}', json={"phrase": "секретный код"})
    assert after_delete.status_code == 400
    assert after_delete.json()['err_message'] == "указанный ключ отсутствует!"


def test_wrong_phrase():
    """
    Указана неверная кодовая фраза при попытке доступа к секрету
    """
    result = simple_post(
        f'{server_url}/generate',
        "Some message",
        "my secret key",
        seconds=10
    )
    assert result.status == 201
    check = requests.get(f'{server_url}/secrets/{result.message}', json={"phrase": "other key"})
    assert check.status_code == 403
    assert check.json()["err_message"] == "неверная кодовая фраза!"


if __name__ == '__main__':
    pytest.main()
