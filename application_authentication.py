import json

from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models_user import database, User  # objBaze
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from sqlalchemy import and_
import re
from decorator import roleCheck


application = Flask(__name__)  # obj app, Flask, name-ime modula
application.config.from_object(Configuration)

jwt = JWTManager(application)


# POSTMAN: http://127.0.0.1:5002/register
@application.route("/register", methods=["POST"])
def register():
    jmbg = request.json.get("jmbg", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    jmbgEmpty = len(jmbg) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0
    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    # missing field check:
    if jmbgEmpty:
        return Response(json.dumps({
            "message": "Field jmbg is missing."
        }), status=400)
    if forenameEmpty:
        return Response(json.dumps({
            "message": "Field forename is missing."
        }), status=400)
    if surnameEmpty:
        return Response(json.dumps({
            "message": "Field surname is missing."
        }), status=400)
    if emailEmpty:
        return Response(json.dumps({
            "message": "Field email is missing."
        }), status=400)
    if passwordEmpty:
        return Response(json.dumps({
            "message": "Field password is missing."
        }), status=400)

    # jmbg check:
    dan = int(jmbg[0:2])
    mesec = int(jmbg[2:4])
    godina = int(jmbg[4:7])
    reg = int(jmbg[7:9])
    kontrola = int(jmbg[12:13])

    months = {
        1: 31,
        2: 28,  # PROVERITI!
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }

    if dan > months[mesec] or dan < 1:
        return Response(json.dumps({"message": "Invalid jmbg."}), status=400)
    if mesec < 1 or mesec > 12:
        return Response(json.dumps({"message": "Invalid jmbg."}), status=400)
    if reg < 70 or reg > 99:
        return Response(json.dumps({"message": "Invalid jmbg."}), status=400)
    proveraFormula = 11 - ((7 * (int(jmbg[0]) + int(jmbg[6])) + 6 * (int(jmbg[1]) + int(jmbg[7])) + 5 * (int(jmbg[2])
        + int(jmbg[8])) + 4 * (int(jmbg[3]) + int(jmbg[9])) + 3 * (int(jmbg[4]) + int(jmbg[10]))
        + 2 * (int(jmbg[5]) + int(jmbg[11]))) % 11)

    if proveraFormula > 9:
        if kontrola != 0:
            return Response(json.dumps({"message": "Invalid jmbg."}), status=400)
    if kontrola != proveraFormula:
        return Response(json.dumps({"message": "Invalid jmbg."}), status=400)

    # forename check:
    if len(forename) > 256:
        return Response(json.dumps({"message": "Invalid forename."}), status=400)

    # surname check:
    if len(surname) > 256:
        return Response(json.dumps({"message": "Invalid surname."}), status=400)

    # email check:
    if len(email) > 256:
        return Response(json.dumps({"message": "Invalid email."}))
    if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    # password check:
    if len(password) > 256 or len(password) < 8:
        return Response(json.dumps({"message": "Invalid password."}), status=400)
    if not any(char.isdigit() for char in password):
        return Response(json.dumps({"message": "Invalid password."}), status=400)
    if not (char.islower() for char in password):
        return Response(json.dumps({"message": "Invalid password."}), status=400)
    if not (char.isupper() for char in password):
        return Response(json.dumps({"message": "Invalid password."}), status=400)

    # email already exists check:
    allUsers = User.query.all()
    for userPom in allUsers:
        if userPom.email == email:
            return Response(json.dumps({"message": "Email already exists."}), status=400)

    # dodavanje u bazu:
    user = User(jmbg=jmbg, forename=forename, surname=surname, email=email, password=password, role="zvanicnik")
    database.session.add(user)
    database.session.commit()

    # TODO: OBRISATI PORUKU, TREBA SAMO STATUS
    return Response(json.dumps({"message": "Registration successful!"}), status=200)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    # missing field check:
    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)
    if passwordEmpty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    # invalid email check:
    if len(email) > 256:
        return Response(json.dumps({"message": "Invalid email."}))
    if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    # invalid credentials check:
    # users = User.query.all()
    # flagFind = False
    # flagFind_wrongPass = False
    # for userPom in users:
    #    if userPom.email == email:
    #        flagFind = True
    #    if userPom.email == email and userPom.password == password:
    #        flagFind_wrongPass = True
    # if not flagFind:
    #    return Response("Invalid credentials.", status=400)
    # if not flagFind_wrongPass:
    #    return Response("Invalid credentials.", status=400)  # wrong password

    # User search:
    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    # invalid credentials check:
    if not user:  # korisnik ne postoji
        return Response(json.dumps({"message": "Invalid credentials."}), status=400)

    additionalClaims = {  # MZD DODATI PASSWORD?
        "forename": user.forename,
        "surname": user.surname,
        "role": user.role,
        "jmbg": user.jmbg
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    return jsonify(accessToken=accessToken, refreshToken=refreshToken)  # STATUS=200 FALI??? - samo dodeli(postman)


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()  # SUBJECT
    refreshClaims = get_jwt()  # PAYLOAD

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "role": refreshClaims["role"],
        "jmbg": refreshClaims["jmbg"]
    }

    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additionalClaims))


@application.route("/delete", methods=["POST"])
@roleCheck(role="admin")
def delete():
    email = request.json.get("email", "")

    # email empty check:
    emailEmpty = len(email) == 0
    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    # invalid email check:
    if len(email) > 256:
        return Response(json.dumps({"message": "Invalid email."}))
    if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    # search user:
    flagFind = True
    users = User.query.all()
    for userPom in users:
        if userPom.email == email:
            flagFind = False

    if flagFind == True:
        return Response(json.dumps({"message": "Unknown user."}), status=400)

    # delete:
    User.query.filter_by(email=email).delete()
    database.session.commit()

    return Response(json.dumps({"message": "Deletion successful"}), status=200)  # OBRISI PORUKU

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)