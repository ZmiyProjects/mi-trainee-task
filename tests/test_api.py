import requests
import pytest
from collections import namedtuple
from time import sleep
import json

RequestResult = namedtuple("RequestResult", ["status", "message"])

@pytest.fixture
def server():
    def _server():
        with open("test_config.json") as  reader:
            conf = json.load(reader)
        return f'http://{conf["host"]}:{conf["port"]}'
    return _server


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


def test_incorrect_insert(server):
    """
    Попытка сохранения пустой структуры вместо секрета
    """
    struct = {}
    result = requests.post(f'{server()}/generate', json=struct)
    assert result.status_code == 400


def test_simple_post(server):
    """
    Проверка сохранения и получения секрета
    """
    result = simple_post(
        f'{server()}/generate',
        "Невероятно важное сообщение!",
        "секретный код",
        seconds=10
    )
    assert result.status == 201
    check = requests.get(f'{server()}/secrets/{result.message}', json={"phrase": "секретный код"})
    assert check.status_code == 200
    assert check.json()["data"] == "Невероятно важное сообщение!"


def test_delete_date(server):
    """
    Попытка сохранения секрета с некорректной датой удаления
    """
    result = simple_post(
        f'{server()}/generate',
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
        f'{server()}/generate',
        "Some message",
        "my secret key",
        seconds=10
    )
    assert result.status == 201
    check = requests.get(f'{server()}/secrets/{result.message}', json={"phrase": "my secret key"})
    assert check.status_code == 200
    assert check.json()["data"] == "Some message"
    after_delete = requests.get(f'{server()}/secrets/{result.message}', json={"phrase": "my secret key"})
    assert after_delete.status_code == 400
    assert after_delete.json()['err_message'] == "указанный ключ отсутствует!"


def test_wrong_phrase(server):
    """
    Указана неверная кодовая фраза при попытке доступа к секрету
    """
    result = simple_post(
        f'{server()}/generate',
        "Some message",
        "my secret key",
        seconds=10
    )
    assert result.status == 201
    check = requests.get(f'{server()}/secrets/{result.message}', json={"phrase": "other key"})
    assert check.status_code == 403
    assert check.json()["err_message"] == "неверная кодовая фраза!"


if __name__ == '__main__':
    pytest.main()
