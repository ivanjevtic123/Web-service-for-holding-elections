import json
from flask import Flask, request, Response, jsonify
from models_elections import databaseElections, Elections, Participant, ParticipantInElections
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from sqlalchemy import and_
import re
from decorator import roleCheck
from datetime import timedelta, datetime
from dateutil import parser
from configuration_elections import ConfigurationElections
import pytz


application = Flask(__name__)
application.config.from_object(ConfigurationElections)

jwt = JWTManager(application)


@application.route("/createParticipant", methods=["POST"])
@roleCheck(role="admin")
def createParticipant():
    name = request.json.get("name", "")
    individual = request.json.get("individual", "")

    # missing field check:
    nameEmpty = len(name) == 0
    # individualEmpty = len(individual) == 0
    if nameEmpty:
        return Response(json.dumps({"message": "Field name is missing."}), status=400)
    if individual == '':
        return Response(json.dumps({"message": "Field individual is missing."}), status=400)

    # database insertion:
    participant = Participant(name=name, individual=individual)
    databaseElections.session.add(participant)
    databaseElections.session.commit()

    return jsonify(id=participant.id)


@application.route("/getParticipants", methods=["GET"])
@roleCheck(role="admin")
def getParticipants():
    participantsArray = []
    participantsAll = Participant.query.all()
    for p in participantsAll:
        curr = {
            "id": p.id,
            "name": p.name,
            "individual": p.individual
        }
        participantsArray.append(curr)

    return jsonify(participants=participantsArray)


@application.route("/createElection", methods=["POST"])
@roleCheck(role="admin")
def createElection():
    start = request.json.get("start", "")
    end = request.json.get("end", "")
    individual = request.json.get("individual", "")
    participants = request.json.get("participants", "")

    # missing field check:
    startEmpty = len(start) == 0
    endEmpty = len(end) == 0
    # individualEmpty = len(individual) == 0
    participantsEmpty = len(participants) == 0
    if startEmpty:
        return Response(json.dumps({"message": "Field start is missing."}), status=400)
    if endEmpty:
        return Response(json.dumps({"message": "Field end is missing."}), status=400)
    if individual == '':
        return Response(json.dumps({"message": "Field individual is missing."}), status=400)
    if participants == '':
        return Response(json.dumps({"message": "Field participants is missing."}), status=400)


    # Invalid date and time check:
    try:
        startParsed = parser.isoparse(start)
        endParsed = parser.isoparse(end)
    except:
        return Response(json.dumps({"message": "Invalid date and time."}), status=400)
    if end <= start:
        return Response(json.dumps({"message": "Invalid date and time."}), status=400)

    electionsList = Elections.query.all()
    pom = pytz.UTC
    startParsed = startParsed.replace(tzinfo=pom)
    endParsed = endParsed.replace(tzinfo=pom)

    for element in electionsList:
        elStartParsed = parser.isoparse(element.start)
        elStartParsed = elStartParsed.replace(tzinfo=pom)
        elEndParsed = parser.isoparse(element.end)
        elEndParsed = elEndParsed.replace(tzinfo=pom)
        if endParsed > elStartParsed and endParsed < elEndParsed:
            return Response(json.dumps({"message": "Invalid date and time."}), status=400)
        if startParsed > elStartParsed and startParsed < elEndParsed:
            return Response(json.dumps({"message": "Invalid date and time."}), status=400)

    # Invalid participant check:
    if len(participants) < 2:
        return Response(json.dumps({"message": "Invalid participants."}), status=400)
    # TODO: DEO ZA PRIJAVU NA ODG IZBORE PROVERA => DONE
    participantsPomArray = Participant.query.all()
    try:
        int(participants[1])
        for el in participantsPomArray:
            for elPar in participants:
                if elPar == el.id:
                    if el.individual != individual:
                        return Response(json.dumps({"message": "Invalid participants."}), status=400)
    except TypeError:
        return Response(json.dumps({"message": "Invalid participants."}), status=400)

    # Database insertion:
    election = Elections(start=start, end=end, individual=individual)  # election.id
    databaseElections.session.add(election)
    databaseElections.session.commit()

    # PollNumbers creation:
    index = 0
    arrayPom = []
    for curr in participants:
        # Database insertion(Participant in elections):
        participantInElections = ParticipantInElections(participantId=curr, electionsId=election.id)
        databaseElections.session.add(participantInElections)
        databaseElections.session.commit()
        # pollNumbers creation:
        index = index + 1
        arrayPom.append(index)

    return jsonify(pollNumbers=arrayPom)


@application.route("/getElections", methods=["GET"])
@roleCheck(role="admin")
def getElections():
    electionsAll = Elections.query.all()
    participantsArray = []
    electionsArray = []
    for element in electionsAll:
        for par in element.participant:
            participantsArray.append({
                "id": par.id,
                "name": par.name
            })
            electionsArray.append({
                "id": element.id,
                "start": element.start,
                "end": element.end,
                "individual": element.individual,
                "participants": participantsArray
            })
            participantsArray = []

    return jsonify(elections=electionsArray)


# /getResults?id=<ELECTION_ID>
@application.route("/getResults_1", methods=["GET"])
@roleCheck(role="admin")
def getResults_1():
    electionId = request.args.get("id", "")
    electionIdEmpty = len(electionId) == 0
    if electionIdEmpty:
        return Response(json.dumps({"message": "Field id is missing."}), status=400)
    if len(Elections.query.filter(Elections.id == electionId).all()) == 0:
        return Response(json.dumps({"message": "Election does not exist."}), status=400)

    # Election is ongoing check:
    electionsArray = Elections.query.all()
    addHours = timedelta(hours=2)
    currTime = parser.isoparse(datetime.now().isoformat()) + addHours
    for elem in electionsArray:
        startTime = parser.isoparse(elem.start)
        endTime = parser.isoparse(elem.end)
        if startTime < currTime < endTime:
            return Response(json.dumps({"message": "Election is ongoing."}), status=400)

    # CREATING RESULTS:
    electionsFiltered = Elections.query.filter(Elections.id == electionId).first()

    votesPom = electionsFiltered.voices
    gainedVotes = []
    participantsPom = electionsFiltered.participant
    for i in range(len(participantsPom)):
        gainedVotes.append(0)
    for vPom in votesPom:
        if vPom.valide == True:
            gainedVotes[vPom.pollNumber - 1] = gainedVotes[vPom.pollNumber - 1] + 1

    invalidVotesPom = []
    votesCnt = 0
    for vPom_2 in votesPom:
        if vPom_2.valide == True:
            votesCnt += 1
        else:
            invalidVotesPom.append(vPom_2)

    mandatesArray = []
    if electionsFiltered.individual == False:  # Mandates count:
        pom = 0
        cur_j = 0
        for i in range(len(gainedVotes)):
            mandatesArray.append(1)
            if gainedVotes[i] * 20 < votesCnt:
                gainedVotes[i] = 0
        for i in range(250):
            for j in range(len(gainedVotes)):
                if pom < (float(gainedVotes[j]) / float(mandatesArray[j])):
                    cur_j = j
                    pom = float(gainedVotes[j]) / float(mandatesArray[j])
            pom = 0
            mandatesArray[cur_j] += 1
        for i in range(len(gainedVotes)):
            mandatesArray[i] -= 1
    else:  # Predsednicki
        for i in range(len(gainedVotes)):
            if int(gainedVotes[i]) != 0:
                mandatesArray.append(int(gainedVotes[i]) / int(votesCnt))
            else:
                mandatesArray.append(0)

    # JSON RESULT CREATION:
    invalidVotesArray = []
    for elInvalid in invalidVotesPom:
        invalidVotesArray.append({
            "electionOfficialJmbg": elInvalid.electionOfficialJmbg,
            "ballotGuid": elInvalid.guid,
            "pollNumber": elInvalid.pollNumber,
            "reason": elInvalid.reason
        })

    participantsArray = []
    ind = 0
    if electionsFiltered.individual == False:  # parlamentarni:
        for el in participantsPom:
            participantsArray.append({
                "pollNumber": ind + 1,
                "name": el.name,
                "result": mandatesArray[ind]
            })
            ind = ind + 1
    else:
        for el in participantsPom:
            participantsArray.append({
                "pollNumber": ind + 1,
                "name": el.name,
                "result": float("{:.2f}".format(mandatesArray[ind]))
            })
            ind = ind + 1

    return jsonify(participants=participantsArray, invalidVotes=invalidVotesArray)


@application.route("/getResults", methods=["GET"])
@roleCheck(role="admin")
def getResults():
    req_data = request.args
    if not req_data:
        return Response(json.dumps({"message": "Field id is missing."}), status=400)
    if "id" in req_data:
        electionId = request.args["id"]
    else:
        return Response(json.dumps({"message": "Field id is missing."}), status=400)

        # Election is ongoing check:
        electionsArray = Elections.query.all()
        addHours = timedelta(hours=2)
        currTime = parser.isoparse(datetime.now().isoformat()) + addHours
        for elem in electionsArray:
            startTime = parser.isoparse(elem.start)
            endTime = parser.isoparse(elem.end)
            if startTime < currTime < endTime:
                return Response(json.dumps({"message": "Election is ongoing."}), status=400)

        # CREATING RESULTS:
        electionsFiltered = Elections.query.filter(Elections.id == electionId).first()

        votesPom = electionsFiltered.voices
        gainedVotes = []
        participantsPom = electionsFiltered.participant
        for i in range(len(participantsPom)):
            gainedVotes.append(0)
        for vPom in votesPom:
            if vPom.valide == True:
                gainedVotes[vPom.pollNumber - 1] = gainedVotes[vPom.pollNumber - 1] + 1

        invalidVotesPom = []
        votesCnt = 0
        for vPom_2 in votesPom:
            if vPom_2.valide == True:
                votesCnt += 1
            else:
                invalidVotesPom.append(vPom_2)

        mandatesArray = []
        if electionsFiltered.individual == False:  # Mandates count:
            pom = 0
            cur_j = 0
            for i in range(len(gainedVotes)):
                mandatesArray.append(1)
                if gainedVotes[i] * 20 < votesCnt:
                    gainedVotes[i] = 0
            for i in range(250):
                for j in range(len(gainedVotes)):
                    if pom < (float(gainedVotes[j]) / float(mandatesArray[j])):
                        cur_j = j
                        pom = float(gainedVotes[j]) / float(mandatesArray[j])
                pom = 0
                mandatesArray[cur_j] += 1
            for i in range(len(gainedVotes)):
                mandatesArray[i] -= 1
        else:  # Predsednicki
            for i in range(len(gainedVotes)):
                if int(gainedVotes[i]) != 0:
                    mandatesArray.append(int(gainedVotes[i]) / int(votesCnt))
                else:
                    mandatesArray.append(0)

        # JSON RESULT CREATION:
        invalidVotesArray = []
        for elInvalid in invalidVotesPom:
            invalidVotesArray.append({
                "electionOfficialJmbg": elInvalid.electionOfficialJmbg,
                "ballotGuid": elInvalid.guid,
                "pollNumber": elInvalid.pollNumber,
                "reason": elInvalid.reason
            })

        participantsArray = []
        ind = 0
        if electionsFiltered.individual == False:  # parlamentarni:
            for el in participantsPom:
                participantsArray.append({
                    "pollNumber": ind + 1,
                    "name": el.name,
                    "result": mandatesArray[ind]
                })
                ind = ind + 1
        else:
            for el in participantsPom:
                participantsArray.append({
                    "pollNumber": ind + 1,
                    "name": el.name,
                    "result": float("{:.2f}".format(mandatesArray[ind]))
                })
                ind = ind + 1

        return jsonify(participants=participantsArray, invalidVotes=invalidVotesArray)



if __name__ == "__main__":
    databaseElections.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=6002)