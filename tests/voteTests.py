import datetime
import sys;
import time;

from requests  import request;
from utilities import equals;
from utilities import runTests;
from utilities import areEqual;
from utilities import adminLogin;
from utilities import userLogin;
from utilities import addParticipants;
from utilities import setUpAuthorizationErrorRequest;
from utilities import setUpAddElectionData;
from utilities import setUpAdminHeaders;
from utilities import setUpUserHeaders;
from dateutil  import parser;
from data      import getIndividuals;
from data      import setIndividualsAdded;
from data      import getPoliticalParties;
from data      import getIndividualsAdded;
from data      import getPoliticalPartiesAdded;
from data      import setPoliticalPartiesAdded;
from data      import getPresidentialElection;
from data      import getParliamentaryElection;
from data      import updatePresidetialElectionTimes;
from data      import updateParliamentaryElectionTimes;
from data      import getPresidentialElectionAdded;
from data      import getParliamentaryElectionAdded;
from data      import setPresidentialElectionAdded;
from data      import setParliamentaryElectionAdded;
from data      import getGuids;
from data      import getPresidentialElectionResults;
from data      import getParliamentaryElectionResults;
from data      import getInvalidPresidentialElectionPollNumberGuid;

PATH = "temp.csv";

def setUpFile ( path, content ):
    with open ( path, "w" ) as file:
        file.write ( content );

def setUpFirstVoteErrorTest ( withAuthentication, authenticationAddress ):
    def setUpFirstVoteErrorTestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            userLogin ( authenticationAddress, headers );

        lines = "28f8a8e0-f4c7-4e3f-93fb-2f95c53bfe4b";

        setUpFile ( PATH, lines );
        file          = open ( PATH, "r" );
        files["file"] = file;

        return (url, "", False );

    return setUpFirstVoteErrorTestImplementation;

def setUpSecondVoteErrorTest ( withAuthentication, authenticationAddress ):
    def prepareSecondVoteErrorTestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            userLogin ( authenticationAddress, headers );

        lines = "28f8a8e0-f4c7-4e3f-93fb-2f95c53bfe4b, a";

        setUpFile ( PATH, lines );

        file          = open ( PATH, "r" );
        files["file"] = file;

        return (url, "", False);

    return prepareSecondVoteErrorTestImplementation;

def setUpThirdVoteErrorTest ( withAuthentication, authenticationAddress ):
    def setUpThirdVoteErrorTestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            userLogin ( authenticationAddress, headers );

        lines = "28f8a8e0-f4c7-4e3f-93fb-2f95c53bfe4b, -1";

        setUpFile ( PATH, lines );

        file          = open ( PATH, "r" );
        files["file"] = file;

        return (url, "", False);

    return setUpThirdVoteErrorTestImplementation;

def createElection ( withAuthentication, authenticationAddress, administratorAddress, updateElectionTimeFunction, getElectionFunction, setElectionAddedFunction, getParticipnatsFunction, getParticipantsAddFunction, setParticipantsAddedFunction ):
    headers = { };
    if (withAuthentication):
        adminLogin ( authenticationAddress, headers );

    if (not getParticipantsAddFunction ( )):
        addParticipants ( withAuthentication, authenticationAddress, administratorAddress, getParticipnatsFunction, setParticipantsAddedFunction );

    data = { };

    pollNumbers = setUpAddElectionData ( data, updateElectionTimeFunction, getElectionFunction, getParticipnatsFunction );

    response = request (
            method  = "post",
            url     = administratorAddress + "/createElection",
            headers = headers,
            json    = data
    );

    response = request (
            method  = "get",
            url     = administratorAddress + "/getElections",
            headers = headers
    );

    elections = response.json ( )["elections"];

    for election in elections:
        if ( election["individual"] == getElectionFunction ( )["individual"] ):
            getElectionFunction ( )["id"] = election["id"];
            break;

    setElectionAddedFunction ( True );

    return pollNumbers;

def setUpPresidentialElectionTest ( withAuthentication, authenticationAddress, administratorAddress, electionStart ):
    def setUpPresidentalElectionTestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            userLogin ( authenticationAddress, headers );

        pollNumbers = [ ];
        for i in range ( len ( getIndividuals ( ) ) ):
            pollNumbers.append ( i + 1 );

        if (electionStart is None):
            if (not getPresidentialElectionAdded ( )):
                pollNumbers = createElection ( withAuthentication, authenticationAddress, administratorAddress, updatePresidetialElectionTimes, getPresidentialElection, setPresidentialElectionAdded, getIndividuals, getIndividualsAdded, setIndividualsAdded );
        else:
            getPresidentialElection ( )["start"] = electionStart;

        presidentialElection = getPresidentialElection ( );

        start = parser.isoparse ( presidentialElection["start"] );
        seconds = (start - datetime.datetime.now ( ) ).total_seconds ( );
        if ( seconds < 0 ):
            seconds = 0;
        time.sleep ( seconds );


        guids    = getGuids ( );
        ballots  = guids[:len ( guids ) // 2];
        length   = len ( ballots );
        ballotsA = ballots[:length // 3];
        ballotsB = ballots[length // 3 : 2 * length // 3];
        ballotsC = ballots[2 * length // 3:];

        with open ( PATH, "w" ) as file:
            for ballot in ballotsA:
                file.write ( ballot + "," + str ( pollNumbers[0] ) + "\n" );

            for ballot in ballotsB:
                file.write ( ballot + "," + str ( pollNumbers[1] ) + "\n" );

            for ballot in ballotsC:
                file.write ( ballot + "," + str ( pollNumbers[2] ) + "\n" );

            file.write ( ballotsC[-1] + "," + str ( pollNumbers[0] ) + "\n" );

            file.write ( getInvalidPresidentialElectionPollNumberGuid ( ) + "," + "5" + "\n" );

        file = open ( PATH, "r" );
        files["file"] = file;

        return (url, "", False);

    return setUpPresidentalElectionTestImplementation;

def setUpParliamentaryElection ( withAuthentication, authenticationAddress, administratorAddress, electionStart ):
    def setUpParliamentaryElectionImplementation ( url, headers, data, files ):
        if (withAuthentication):
            userLogin ( authenticationAddress, headers );

        pollNumbers = [ ];
        for i in range ( len ( getPoliticalParties ( ) ) ):
            pollNumbers.append ( i + 1 );

        if (electionStart is None):
            if (not getParliamentaryElectionAdded ( )):
                pollNumbers = createElection ( withAuthentication, authenticationAddress, administratorAddress, updateParliamentaryElectionTimes, getParliamentaryElection, setParliamentaryElectionAdded, getPoliticalParties, getPoliticalPartiesAdded, setPoliticalPartiesAdded );
        else:
            getParliamentaryElection ( )["start"] = electionStart;

        parliamentaryElection = getParliamentaryElection ( );

        start = parser.isoparse ( parliamentaryElection["start"] );
        seconds = (start - datetime.datetime.now ( ) ).total_seconds ( );
        if ( seconds < 0 ):
            seconds = 0;
        time.sleep ( seconds );


        guids   = getGuids ( );
        ballots = guids[len ( guids ) // 2:];

        endA = 20;
        endB = endA + 80;
        endC = endB + 100;
        endD = endC + 100;
        endE = endD + 200;

        with open ( PATH, "w" ) as file:
            for ballot in ballots[:endA]:
                file.write ( ballot + "," + str ( pollNumbers[0] ) + "\n" );

            for ballot in ballots[endA:endB]:
                file.write ( ballot + "," + str ( pollNumbers[1] ) + "\n" );

            for ballot in ballots[endB:endC]:
                file.write ( ballot + "," + str ( pollNumbers[2] ) + "\n" );

            for ballot in ballots[endC:endD]:
                file.write ( ballot + "," + str ( pollNumbers[3] ) + "\n" );

            for ballot in ballots[endD:]:
                file.write ( ballot + "," + str ( pollNumbers[4] ) + "\n" );


        file = open ( PATH, "r" );
        files["file"] = file;

        return (url, "", False);

    return setUpParliamentaryElectionImplementation;

def setUpGetResultsRequest ( withAuthentication, authenticationAddress, getElectionFunction, electionId, electionEnd ):
    def setUpGetResultsRequestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            adminLogin ( authenticationAddress, headers );

        end = datetime.datetime.now ( );
        if (electionEnd is None):
            end = parser.isoparse ( getElectionFunction ( )["end"] );
        else:
            end = parser.isoparse ( electionEnd );

        seconds = (end - datetime.datetime.now ( )).total_seconds ( );

        if (seconds < 0):
            seconds = 0;
        time.sleep ( seconds );

        id = "";
        if ( electionId is None):
            id = getElectionFunction ( )["id"];
        else:
            id = electionId;

        return (url + str ( id ), "", False);

    return setUpGetResultsRequestImplementation;

def getResultsRequestTest ( getResultsFuntion, electionOfficialJmbg ):
    def getResultsRequestTestImplementation ( setUpData, expectedResponse, receivedResponse ):
        assert "invalidVotes" in receivedResponse, "Invalid response, field invalidVotes is missing.";
        assert "participants" in receivedResponse, "Invalid response, field participants is missing.";

        expectedElectionResults = getResultsFuntion ( );

        expectedInvalidVotes = expectedElectionResults["invalidVotes"];
        expectedParticipants = expectedElectionResults["participants"];

        receivedInvalidVotes = receivedResponse["invalidVotes"];
        receivedParticipants = receivedResponse["participants"];

        if (electionOfficialJmbg is not None):
            for vote in expectedInvalidVotes:
                vote["electionOfficialJmbg"] = electionOfficialJmbg;

        assert areEqual ( expectedInvalidVotes, receivedInvalidVotes ), f"Invalid response, expected invalid votes {expectedInvalidVotes}, received invalid votes {receivedInvalidVotes}.";
        assert areEqual ( expectedParticipants, receivedParticipants ), f"Invalid response, expected participants {expectedParticipants}, received participants {receivedParticipants}.";

    return getResultsRequestTestImplementation;


def setUpGetResultsErrorTest ( withAuthentication, authenticationAddress, presidentialElectionId, parliamentaryElectionId ):
    def setUpGetResultsErrorTestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            adminLogin ( authenticationAddress, headers );

        ids = [ ]
        if (presidentialElectionId is None):
            if (getPresidentialElectionAdded ( )):
                ids.append ( getPresidentialElection ( ) ["id"] );
        else:
            ids.append ( presidentialElectionId );

        if (parliamentaryElectionId is None):
            if (getParliamentaryElectionAdded ( )):
                ids.append ( getParliamentaryElection ( )["id"]);
        else:
            ids.append ( parliamentaryElectionId );

        id = 1;
        while ( id in ids ):
            id = id + 1;

        return (url + str ( id ), "", False);

    return setUpGetResultsErrorTestImplementation;



def runVoteTests ( administratorAddress, stationAddress, withAuthentication, authenticationAddress, presidentialElectionId, presidentialElectionStart, presidentialElectionEnd, parliamentaryElectionId, parliamentaryElectionStart, parliamentaryElectionEnd, electionOfficialJmbg ):

    voteErrorTests = [
            # create election authorization error
            ["post", "/vote", setUpAuthorizationErrorRequest ( withAuthentication )                 , { }, { }, { }, 401, { "msg": "Missing Authorization Header"              }, equals, 1],
            ["post", "/vote", setUpAdminHeaders ( withAuthentication, authenticationAddress )       , { }, { }, { }, 401, { "msg": "Missing Authorization Header"              }, equals, 1],
            ["post", "/vote", setUpUserHeaders ( withAuthentication, authenticationAddress )        , { }, { }, { }, 400, { "message": "Field file is missing."                }, equals, 1],
            ["post", "/vote", setUpFirstVoteErrorTest ( withAuthentication, authenticationAddress ) , { }, { }, { }, 400, { "message": "Incorrect number of values on line 0." }, equals, 1],
            ["post", "/vote", setUpSecondVoteErrorTest ( withAuthentication, authenticationAddress ), { }, { }, { }, 400, { "message": "Incorrect poll number on line 0."      }, equals, 1],
            ["post", "/vote", setUpThirdVoteErrorTest ( withAuthentication, authenticationAddress ) , { }, { }, { }, 400, { "message": "Incorrect poll number on line 0."      }, equals, 1],
    ];

    getResultsErrorTests = [
            # create election authorization error
            ["get", "/getResults"    , setUpAuthorizationErrorRequest ( withAuthentication )                                                                  , { }, { }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],
            ["get", "/getResults"    , setUpUserHeaders ( withAuthentication, authenticationAddress )                                                         , { }, { }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],
            ["get", "/getResults"    , setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                        , { }, { }, { }, 400, { "message": "Field id is missing."     }, equals, 1],
            ["get", "/getResults?id=", setUpGetResultsErrorTest ( withAuthentication, authenticationAddress, presidentialElectionId, parliamentaryElectionId ), { }, { }, { }, 400, { "message": "Election does not exist." }, equals, 1],
    ];

    presidentialElectionVoteTests = [
            ["post", "/vote", setUpPresidentialElectionTest ( withAuthentication, authenticationAddress, administratorAddress, presidentialElectionStart ), { }, { }, { }, 200, None, equals, 2],
    ];

    presidentialElectionGetResultsTests = [
            ["get", "/getResults?id=", setUpGetResultsRequest ( withAuthentication, authenticationAddress, getPresidentialElection, presidentialElectionId, presidentialElectionEnd ), { }, { }, { }, 200, { }, getResultsRequestTest ( getPresidentialElectionResults, electionOfficialJmbg ), 8],
    ];

    parliamentaryElectionVoteTests = [
            ["post", "/vote", setUpParliamentaryElection ( withAuthentication, authenticationAddress, administratorAddress, parliamentaryElectionStart ), { }, { }, { }, 200, None, equals, 2],
    ];

    parliamentaryElectionGetResultsTests = [
            ["get", "/getResults?id=", setUpGetResultsRequest ( withAuthentication, authenticationAddress, getParliamentaryElection, parliamentaryElectionId, parliamentaryElectionEnd ), { }, { }, { }, 200, {  }, getResultsRequestTest ( getParliamentaryElectionResults, electionOfficialJmbg ), 8],
    ];

    tests = [ ];

    for test in getResultsErrorTests:
        test[1] = administratorAddress + test[1];
        tests.append ( test );

    for test in voteErrorTests:
        test[1] = stationAddress + test[1];
        tests.append ( test );

    for test in presidentialElectionVoteTests:
        test[1] = stationAddress + test[1];
        tests.append ( test );

    for test in presidentialElectionGetResultsTests:
        test[1] = administratorAddress + test[1];
        tests.append ( test );

    for test in parliamentaryElectionVoteTests:
        test[1] = stationAddress + test[1];
        tests.append ( test );

    for test in parliamentaryElectionGetResultsTests:
        test[1] = administratorAddress + test[1];
        tests.append ( test );

    percentage = runTests ( tests );

    return percentage;
