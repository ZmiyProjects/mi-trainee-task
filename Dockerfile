FROM python:3.7
WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUM_HOST 0.0.0.0
COPY . /code
RUN pip install --no-cache-dir -r requirements.txt
ADD ./create_db.sql /docker-entrypoint-initdb.d/


