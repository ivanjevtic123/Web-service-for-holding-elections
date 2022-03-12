import sys;

from dateutil  import parser;
from data      import getElectionDuration;
from data      import getIndividuals;
from data      import getIndividualsAdded;
from data      import getParliamentaryElection;
from data      import getPoliticalParties;
from data      import getPoliticalPartiesAdded;
from data      import getPresidentialElection;
from data      import setIndividualsAdded;
from data      import setParliamentaryElectionAdded;
from data      import setPoliticalPartiesAdded;
from data      import setPresidentialElectionAdded;
from data      import updateParliamentaryElectionTimes;
from data      import updatePresidetialElectionTimes;
from utilities import addParticipants;
from utilities import setParticipantIds;
from utilities import adminLogin;
from utilities import areEqual;
from utilities import copyDictionary;
from utilities import equals;
from utilities import setUpAddElectionData;
from utilities import setUpAdminHeaders;
from utilities import setUpUserHeaders;
from utilities import setUpAuthorizationErrorRequest;
from utilities import runTests;


def setUpIndividualElectionErrorTest ( withAuthentication, authenticationAddress, administratorAddress, individualIds, politicalPartyIds ):
    def setUpIndividualElectionErrorTestImplementation ( url, headers, data, files ):
        if (not getIndividualsAdded ( )):
            if (individualIds is None):
                addParticipants ( withAuthentication, authenticationAddress, administratorAddress, getIndividuals, setIndividualsAdded );
            else:
                setParticipantIds ( getIndividuals, setIndividualsAdded, individualIds );

        if (not getPoliticalPartiesAdded ( )):
            if (politicalPartyIds is None):
                addParticipants ( withAuthentication, authenticationAddress, administratorAddress, getPoliticalParties, setPoliticalPartiesAdded );
            else:
                setParticipantIds ( getPoliticalParties, setPoliticalPartiesAdded, politicalPartyIds );

        if (withAuthentication):
            adminLogin ( authenticationAddress, headers );

        ids = [individual["id"] for individual in getIndividuals ( )] + [getPoliticalParties ( )[0]["id"]];

        data["participants"].extend ( ids );

        return (url, "", False);

    return setUpIndividualElectionErrorTestImplementation;

def setUpParliamentaryELectionErrorTest ( withAuthentication, authenticationAddress, administratorAddress, individualIds, politicalPartyIds ):
    def setUpParliamentaryElectionErrorTestImplementation ( url, headers, data, files ):
        if (not getIndividualsAdded ( )):
            if (individualIds is None):
                addParticipants ( withAuthentication, authenticationAddress, administratorAddress, getIndividuals, setIndividualsAdded );
            else:
                setParticipantIds ( getIndividuals, setIndividualsAdded, individualIds );

        if (not getPoliticalPartiesAdded ( )):
            if (individualIds is None):
                addParticipants ( withAuthentication, authenticationAddress, administratorAddress, getPoliticalParties, setPoliticalPartiesAdded );
            else:
                setParticipantIds ( getPoliticalParties, getPoliticalPartiesAdded, politicalPartyIds );

        if (withAuthentication):
            adminLogin ( authenticationAddress, headers );

        ids = [party["id"] for party in getPoliticalParties ( )] + [getIndividuals ( )[0]["id"]];

        data["participants"].extend ( ids );

        return (url, "", False);

    return setUpParliamentaryElectionErrorTestImplementation;

def setUpPresidentialElectionTest ( withAuthentication, authenticationAddress, administratorAddress, individualIds ):
    def setUpPresidentialElectionTestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            adminLogin ( authenticationAddress, headers );

        if (not getIndividualsAdded ( )):
            if (individualIds is None):
                addParticipants ( withAuthentication, authenticationAddress, administratorAddress, getIndividuals, setIndividualsAdded );
            else:
                setParticipantIds ( getIndividuals, setIndividualsAdded, individualIds );

        pollNumbers = setUpAddElectionData ( data, updatePresidetialElectionTimes, getPresidentialElection, getIndividuals );

        return (url, pollNumbers, False);

    return setUpPresidentialElectionTestImplementation;


def setUpParliamentaryElectionTest ( withAuthentication, authenticationAddress, administratorAddress, politicalPartyIds ):
    def setUpParliamentaryElectionTestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            adminLogin ( authenticationAddress, headers );

        if (not getPoliticalPartiesAdded ( )):
            if (politicalPartyIds is None):
                addParticipants ( withAuthentication, authenticationAddress, administratorAddress, getPoliticalParties, setPoliticalPartiesAdded );
            else:
                setParticipantIds ( getPoliticalParties, setPoliticalPartiesAdded, politicalPartyIds );

        pollNumbers = setUpAddElectionData ( data, updateParliamentaryElectionTimes, getParliamentaryElection, getPoliticalParties );

        return (url, pollNumbers, False);

    return setUpParliamentaryElectionTestImplementation;


def createElectionRequestTest ( setElectionAddedFuntion ):
    def createElectionRequestTestImplementation ( pollNumbers, expectedResponse, receivedResponse ):
        assert "pollNumbers" in receivedResponse, "Invalid response, field pollNumbers is missing."

        receivedPollNumbers = receivedResponse["pollNumbers"];

        assert areEqual ( pollNumbers, receivedPollNumbers ), f"Invalid response, expected {pollNumbers}, received {receivedPollNumbers}";

        setElectionAddedFuntion ( True );

    return createElectionRequestTestImplementation;

def setUpGetElectionRequest ( withAuthentication, authenticationAddress, presidentialElectionStart, presidentialElectionEnd, parliamentaryElectionStart, parliamentaryElectionEnd ):
    def setUpGetElectionRequestTestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            adminLogin ( authenticationAddress, headers );

        if ( presidentialElectionStart and presidentialElectionEnd and parliamentaryElectionStart and parliamentaryElectionEnd ):
            getPresidentialElection ( )["start"]  = presidentialElectionStart;
            getPresidentialElection ( )["end"]    = presidentialElectionEnd;
            getParliamentaryElection ( )["start"] = parliamentaryElectionStart;
            getParliamentaryElection ( )["end"]   = parliamentaryElectionEnd;

        return (url, "", False);

    return setUpGetElectionRequestTestImplementation;

def getElectionsRequestTest ( setUpData, expectedResponse, receivedResponse ):
    assert "elections" in receivedResponse, "Invalid response, field elections is missing.";

    receivedElections = receivedResponse["elections"];

    assert len ( receivedElections ) == 2, "Invalid response, invalid number of elections.";

    checked = [ ];

    for receivedElection in receivedElections:
        assert "id"           in receivedElection, "Invalid response, field id is missing.";
        assert "start"        in receivedElection, "Invalid response, field start is missing.";
        assert "end"          in receivedElection, "Invalid response, field end is missing.";
        assert "individual"   in receivedElection, "Invalid response, field individual is missing.";
        assert "participants" in receivedElection, "Invalid response, field participants is missing.";

        receivedStart        = parser.isoparse ( receivedElection["start"] );
        receivedEnd          = parser.isoparse ( receivedElection["end"] );
        receivedIndividual   = receivedElection["individual"];
        receivedParticipants = receivedElection["participants"];

        election = getPresidentialElection ( ) if ( receivedIndividual == True ) else getParliamentaryElection ( );

        assert not (receivedElection["id"] in checked), "Invalid response, duplicate id."

        expectedStart        = parser.isoparse ( election["start"] );
        expectedEnd          = parser.isoparse ( election["end"] );
        expectedIndividual   = election["individual"];
        expectedParticipants = election["participants"];

        assert expectedStart      == receivedStart                   , f"Invalid field start for election {receivedElection}, expected {expectedStart}, received {receivedStart}.";
        assert expectedEnd        == receivedEnd                     , f"Invalid field end for election {receivedElection}, expected {expectedEnd}, received {receivedEnd}.";
        assert expectedIndividual == receivedIndividual              , f"Invalid field individual for election {receivedElection}, expected {expectedIndividual}, received {receivedIndividual}.";
        assert areEqual ( receivedParticipants, expectedParticipants ), f"Invalid field participants for election {receivedElection}, expected {expectedParticipants}, received {receivedParticipants}.";

        election["id"] = receivedElection["id"];

        checked.append ( election["id"] );

def setUpOverallapingElectionsErrorTest ( withAuthentication, authenticationAddress, getElectionFunction, operation ):
    def setUpOverallapingElectionsErrorTestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            adminLogin ( authenticationAddress, headers );

        election = getElectionFunction ( );

        copyDictionary ( data, election );

        start         = parser.isoparse ( data["start"] );
        end           = parser.isoparse ( data["end"] );
        duration      = getElectionDuration ( );
        step          = duration / 2;
        start         = operation ( start, step );
        end           = operation ( end, step );
        data["start"] = start.isoformat ( );
        data["end"]   = end.isoformat ( );


        return (url, "", False);

    return setUpOverallapingElectionsErrorTestImplementation;


def runElectionTests ( administratorAddress, withAuthentication, authenticationAddress, individualIds, politicalPartyIds, presidentialElectionStart, presidentialElectionEnd, parliamentaryElectionStart, parliamentaryElectionEnd ):
    tests = [
            # create election authorization error
            ["post", "/createElection", setUpAuthorizationErrorRequest ( withAuthentication )                                                                                    , { }, {                                                                                                                  }, { } , 401, { "msg": "Missing Authorization Header"       }, equals, 1],
            ["post", "/createElection", setUpUserHeaders ( withAuthentication, authenticationAddress )                                                                           , { }, {                                                                                                                  }, { } , 401, { "msg": "Missing Authorization Header"       }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, {                                                                                                                  }, { } , 400, { "message": "Field start is missing."        }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": ""                                                                                                      }, { } , 400, { "message": "Field start is missing."        }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": " "                                                                                                     }, { } , 400, { "message": "Field end is missing."          }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": " "                       , "end": ""                                                                   }, { } , 400, { "message": "Field end is missing."          }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": " "                       , "end": " "                                                                  }, { } , 400, { "message": "Field individual is missing."   }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": " "                       , "end": " "                       , "individual": False                      }, { } , 400, { "message": "Field participants is missing." }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": " "                       , "end": " "                       , "individual": False, "participants": []  }, { } , 400, { "message": "Invalid date and time."         }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": "202106-16T15:55:46+0100" , "end": " "                       , "individual": False, "participants": []  }, { } , 400, { "message": "Invalid date and time."         }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": "2021-06-16T1555460100"   , "end": " "                       , "individual": False, "participants": []  }, { } , 400, { "message": "Invalid date and time."         }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": "2021-06-16T15:55:46+0100", "end": " "                       , "individual": False, "participants": []  }, { } , 400, { "message": "Invalid date and time."         }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": "2021-06-16T15:55:46+0100", "end": "202106-16T16:55:46+0100" , "individual": False, "participants": []  }, { } , 400, { "message": "Invalid date and time."         }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": "2021-06-16T15:55:46+0100", "end": "2021-06-16T1655460100"   , "individual": False, "participants": []  }, { } , 400, { "message": "Invalid date and time."         }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": "2021-06-16T16:55:46+0100", "end": "2021-06-16T15:55:46+0100", "individual": False, "participants": []  }, { } , 400, { "message": "Invalid date and time."         }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": "2021-06-16T15:55:46+0100", "end": "2021-06-16T16:55:46+0100", "individual": False, "participants": []  }, { } , 400, { "message": "Invalid participants."          }, equals, 1],
            ["post", "/createElection", setUpAdminHeaders ( withAuthentication, authenticationAddress )                                                                          , { }, { "start": "2021-06-16T15:55:46+0100", "end": "2021-06-16T16:55:46+0100", "individual": False, "participants": [1] }, { } , 400, { "message": "Invalid participants."          }, equals, 1],
            ["post", "/createElection", setUpIndividualElectionErrorTest ( withAuthentication, authenticationAddress, administratorAddress, individualIds, politicalPartyIds )   , { }, { "start": "2021-06-16T15:55:46+0100", "end": "2021-06-16T16:55:46+0100", "individual": True , "participants": []  }, { } , 400, { "message": "Invalid participants."          }, equals, 1],
            ["post", "/createElection", setUpParliamentaryELectionErrorTest ( withAuthentication, authenticationAddress, administratorAddress, individualIds, politicalPartyIds ), { }, { "start": "2021-06-16T15:55:46+0100", "end": "2021-06-16T16:55:46+0100", "individual": False, "participants": []  }, { } , 400, { "message": "Invalid participants."          }, equals, 1],

            # get elections error
            ["get", "/getElections", setUpAuthorizationErrorRequest ( withAuthentication )         , { }, { }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],
            ["get", "/getElections", setUpUserHeaders ( withAuthentication, authenticationAddress ), { }, { }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],

            # create election
            ["post", "/createElection", setUpPresidentialElectionTest ( withAuthentication, authenticationAddress, administratorAddress, individualIds )     , { }, { }, { }, 200, { }, createElectionRequestTest ( setPresidentialElectionAdded ) , 5],
            ["post", "/createElection", setUpParliamentaryElectionTest ( withAuthentication, authenticationAddress, administratorAddress, politicalPartyIds ), { }, { }, { }, 200, { }, createElectionRequestTest ( setParliamentaryElectionAdded ), 5],

            # get elections
            ["get", "/getElections", setUpGetElectionRequest ( withAuthentication, authenticationAddress, presidentialElectionStart, presidentialElectionEnd, parliamentaryElectionStart, parliamentaryElectionEnd ), { }, { }, { }, 200, { }, getElectionsRequestTest, 4],

            # create election invalid dates
            ["post", "/createElection", setUpOverallapingElectionsErrorTest ( withAuthentication, authenticationAddress, getPresidentialElection, lambda time, step: time - step ) , { }, { }, { }, 400, { "message": "Invalid date and time." }, equals, 2],
            ["post", "/createElection", setUpOverallapingElectionsErrorTest ( withAuthentication, authenticationAddress, getParliamentaryElection, lambda time, step: time + step ), { }, { }, { }, 400, { "message": "Invalid date and time." }, equals, 2],
    ]

    for test in tests:
        test[1] = administratorAddress + test[1];

    percentage = runTests ( tests );

    return percentage;
