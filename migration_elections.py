from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from models_elections import databaseElections
from sqlalchemy_utils import database_exists, create_database
from configuration_elections import ConfigurationElections

application = Flask(__name__)
application.config.from_object(ConfigurationElections)

migrateObject = Migrate(application, databaseElections)

if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
    create_database(application.config["SQLALCHEMY_DATABASE_URI"])

databaseElections.init_app(application)

with application.app_context() as context:
    init()
    migrate(message="Production migration")
    upgrade()
