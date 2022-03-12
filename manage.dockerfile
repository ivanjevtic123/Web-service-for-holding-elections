FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY application_authentication.py ./application_authentication.py
COPY configuration.py ./configuration.py
COPY decorator.py ./decorator.py
COPY manage_authentication.py ./manage_authentication.py
COPY models_user.py ./models_user.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV DATABASE_URL="/opt/src"

ENTRYPOINT ["python", "./manage_authentication.py"]