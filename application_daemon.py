from dateutil import parser
from datetime import datetime, timedelta
import pytz
from flask import Flask
from redis import Redis
from flask_jwt_extended import JWTManager

from configuration_elections import ConfigurationElections
from models_elections import databaseElections, Elections, Voice


application = Flask(__name__)
application.config.from_object(ConfigurationElections)
jwt = JWTManager(application)


@application.route("/", methods=["GET"])
def index():
    return "Wellcome daemon"


def main(vote):
    print(vote)
    pom = pytz.UTC
    vote_data = vote.split("#")

    electionsArray = Elections.query.all()
    currTime = parser.isoparse(datetime.now().isoformat()) + timedelta(hours=2) + timedelta(seconds=1) + timedelta(milliseconds=70)

    electionsId = -1
    electionsOngoing = False
    for el in electionsArray:
        startTime = parser.isoparse(el.start)
        endTime = parser.isoparse(el.end)
        if startTime < currTime < endTime:
            electionsId = el.id
            electionsOngoing = True
            break

    if electionsOngoing == False:
        print("No elections")
        return

    votePom = Voice.query.filter(Voice.guid == vote_data[0]).first()
    if votePom:
        duplicateVote = Voice(
            guid=vote_data[0], electionOfficialJmbg=vote_data[2], valide=False, pollNumber=int(vote_data[1]),
            reason="Duplicate ballot.", electionsId=electionsId
        )
        databaseElections.session.add(duplicateVote)
        databaseElections.session.commit()
    else:
        electionsFiltered = Elections.query.filter(Elections.id == electionsId).first()
        participantsCnt = 0
        for element in electionsFiltered:
            participantsCnt = participantsCnt + 1

        if int(vote_data[1]) > participantsCnt:
            invalidVote = Voice(
                guid=vote_data[0], electionOfficialJmbg=vote_data[2], valide=False, pollNumber=int(vote_data[1]),
                reason="Invalid poll number.", electionsId=electionsId
            )
            databaseElections.session.add(invalidVote)
            databaseElections.session.commit()
        else:
            validVote = Voice(
                guid=vote_data[0], electionOfficialJmbg=vote_data[2], valide=True,
                pollNumber=int(vote_data[1]), electionsId=electionsId
            )
            databaseElections.session.add(validVote)
            databaseElections.session.commit()


# restart: always -- .yaml
# (.yaml)addConfig->Docker-Compose->ComposeFile->development.yaml
# docker swarm init
# docker stack deploy --compose-file deployment_2.yaml swarm_1

# docker swarm leave --force

# imena menjati swarmu
# --type all --authentication-address http://127.0.0.1:5002 --jwt-secret JWT_SECRET_KEY --roles-field role --administrator-role admin --user-role zvanicnik --administrator-address http://127.0.0.1:6002 --station-address http://127.0.0.1:6004 --with-authentication

# http://127.0.0.1:6002/getResults?id=1
# http://127.0.0.1:5002/login

if __name__ == "__main__":
    databaseElections.init_app(application)
    with application.app_context():
        while True:
            with Redis(host=ConfigurationElections.REDIS_HOST) as redis:
                _, message = redis.blpop(ConfigurationElections.REDIS_THREADS_LIST)
                message = message.decode("utf-8")
                print(message)
                main(message)
