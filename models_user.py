from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class User(database.Model):
    __tablename__ = "users"

    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)
    jmbg = database.Column(database.String(256), nullable=False)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)
    password = database.Column(database.String(256), nullable=False)
    role = database.Column(database.String(256), nullable=False)

    def __repr__(self):
        return "({}, {}, {}, {}, {}, {}, {})".format(
            self.id, self.jmbg, self.forename, self.surname, self.email, self.password, self.role
        )
