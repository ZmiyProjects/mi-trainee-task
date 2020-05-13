import requests
import unittest
from collections import namedtuple
from time import sleep
from argparse import ArgumentParser
import sys

RequestResult = namedtuple("RequestResult", ["status", "message"])

args = ArgumentParser()
args.add_argument('-ho', '--host', type=str)
args.add_argument('-p', '--post', type=str)
address = args.parse_args(sys.argv[1:])

server_url = f'http://{address.host}:{address.port}'


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


class Tests(unittest.TestCase):
    def test_delete_by_timer(self):
        """
        Проверка удаления секрета по таймеру
        """
        result = simple_post(
            f'{server_url}/generate',
            "Невероятно важное сообщение!",
            "секретный код",
            seconds=3
        )
        self.assertEqual(result.status, 201)
        sleep(10)
        deleted = requests.get(f'{server_url}/secrets/{result.message}', json={"phrase": "секретный код"})
        self.assertEqual(deleted.status_code, 400)
        self.assertEqual(deleted.json()['err_message'], "указанный ключ отсутствует!")

    def test_incorrect_insert(self):
        """
        Попытка сохранения пустой структуры вместо секрета
        """
        struct = {}
        result = requests.post(f'{server_url}/generate', json=struct)
        self.assertEqual(result.status_code, 400)

    def test_simple_post(self):
        """
        Проверка сохранения и получения секрета
        """
        result = simple_post(
            f'{server_url}/generate',
            "Невероятно важное сообщение!",
            "секретный код",
            seconds=10
        )
        self.assertEqual(result.status, 201)
        check = requests.get(f'{server_url}/secrets/{result.message}', json={"phrase": "секретный код"})
        self.assertEqual(check.status_code, 200)
        self.assertEqual(check.json()["data"], "Невероятно важное сообщение!")

    def test_delete_date(self):
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
        self.assertEqual(result.status, 400)
        self.assertEqual(result.message, "Некорректная дата удаления!")

    def test_del_after_get(self):
        """
        Попытка доступа к удаленному секрету
        """
        result = simple_post(
            f'{server_url}/generate',
            "Some message",
            "my secret key",
            seconds=10
        )
        self.assertEqual(result.status, 201)
        check = requests.get(f'{server_url}/secrets/{result.message}', json={"phrase": "my secret key"})
        self.assertEqual(check.status_code, 200)
        self.assertEqual(check.json()["data"], "Some message")
        after_delete = requests.get(f'{server_url}/secrets/{result.message}', json={"phrase": "секретный код"})
        self.assertEqual(after_delete.status_code, 400)
        self.assertEqual(after_delete.json()['err_message'], "указанный ключ отсутствует!")

    def test_wrong_phrase(self):
        """
        Указана неверная кодовая фраза при попытке доступа к секрету
        """
        result = simple_post(
            f'{server_url}/generate',
            "Some message",
            "my secret key",
            seconds=10
        )
        self.assertEqual(result.status, 201)
        check = requests.get(f'{server_url}/secrets/{result.message}', json={"phrase": "other key"})
        self.assertEqual(check.status_code, 403)
        self.assertEqual(check.json()["err_message"], "неверная кодовая фраза!")


if __name__ == '__main__':
    unittest.main()