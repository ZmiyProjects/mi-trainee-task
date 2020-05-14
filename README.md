# Как запустить?

Скопировать на локальное устройство и запустить контейнер в корневой директории проекта:

git clone https://github.com/ZmiyProjects/mi-trainee-task
sudo docker-compose up

с текущими настройками веб-сервис запускается на 0.0.0.0:8080

# Запуск тестов

Для запуска понадобится виртуальное окружение python3.7 с установленными модулями pytest и request

```sh
cd tests/
python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

Файл test_config.json содержит конфигурацию (хост и порт) для запуска тестов, по умолчанию это:

```json
{
    "host": "0.0.0.0",
    "port": "8080"
}
```
