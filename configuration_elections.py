from datetime import timedelta
import os

databaseUrl = os.environ["DATABASE_URL"]

red = os.environ["REDIS"]

class ConfigurationElections():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/admin"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    REDIS_HOST = red
    REDIS_THREADS_LIST = "voice"
