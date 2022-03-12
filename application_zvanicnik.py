import csv
import io
import json

from flask import Flask, request, jsonify, Response
from redis import Redis
from configuration_elections import ConfigurationElections
from models_elections import databaseElections
from decorator import roleCheck
from flask_jwt_extended import JWTManager, get_jwt


application = Flask(__name__)
application.config.from_object(ConfigurationElections)

jwt = JWTManager(application)


@application.route("/vote", methods=["POST"])
@roleCheck(role="zvanicnik")
def vote():
    inputFile = request.files.get("file", "")
    if not inputFile:
        return Response(json.dumps({"message": "Field file is missing."}), status=400)
    inputFile = inputFile.stream.read().decode("utf-8")
    streamPom = io.StringIO(inputFile)
    readerPom = csv.reader(streamPom)
    commentsArray = []
    additionalClaims = get_jwt()
    jmbg = additionalClaims["electionOfficialJmbg"]  # electionOfficialJmbg

    lineNumber = -1
    for rowPom in readerPom:
        lineNumber = lineNumber + 1
        if len(rowPom) != 2:
            return Response(json.dumps({"message": "Incorrect number of values on line {}.".format(lineNumber)}), status=400)
        flag = True
        try:
            int(rowPom[1])
            flag = True
        except ValueError:
            flag = False
        if not int(rowPom[1]) > 0 or not flag:
            return Response(json.dumps({"message": "Incorrect poll number on line {}.".format(lineNumber)}), status=400)
        commentsArray.append(rowPom[0] + "#" + rowPom[1] + "#" + jmbg)

    with Redis(host=ConfigurationElections.REDIS_HOST, decode_responses=True) as redis:
        for el in commentsArray:
            redis.rpush(ConfigurationElections.REDIS_THREADS_LIST, el)

    return Response(status=200)


if __name__ == "__main__":
    databaseElections.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=6004)