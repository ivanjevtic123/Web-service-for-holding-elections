FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY application_zvanicnik.py ./application_zvanicnik.py
COPY configuration_elections.py ./configuration_elections.py
COPY decorator.py ./decorator.py
COPY models_elections.py ./models_elections.py
COPY migration_elections.py ./migration_elections.py
# COPY demon.py ./application_daemon.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV DATABASE_URL="/opt/src"

ENTRYPOINT ["python", "./application_zvanicnik.py"]