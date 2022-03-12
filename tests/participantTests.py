import sys;

from utilities import runTests;
from utilities import equals;
from utilities import areEqual;
from utilities import adminLogin;
from utilities import setUpAuthorizationErrorRequest;
from utilities import setUpAdminHeaders;
from utilities import setUpUserHeaders;
from data      import getIndividuals;
from data      import getPoliticalParties;
from data      import setIndividualsAdded;
from data      import setPoliticalPartiesAdded;

def setUpCreateParticipantRequest ( withAuthentication, authenticationAddress, index, getParticipantsFunction ):
    def setUpCreateParticipantRequestImplementation ( url, headers, data, files ):
        if (withAuthentication):
            adminLogin ( authenticationAddress, headers );

        data["name"]       = getParticipantsFunction ( )[index]["name"];
        data["individual"] = getParticipantsFunction ( )[index]["individual"];

        return (url, None, False);

    return setUpCreateParticipantRequestImplementation;

def createParticipantRequestTest ( index, getParticipantsFunction ):
    def createParticipantTestImplementation ( setUpData, expectedResponse, receivedResponse ):

        assert "id" in receivedResponse, "Invalid response, field id is missing."

        getParticipantsFunction ( )[index]["id"] = int ( receivedResponse["id"] );

    return createParticipantTestImplementation;

def getParticipantsRequestTest ( individualIds, politicalPartyIDs ):
    def getParticipantsRequestTestImplementation ( setUpData, expectedResponse, receivedResponse ):

        assert "participants" in receivedResponse, "Invalid response, field participants is missing."

        receivedParticipants = receivedResponse["participants"];

        individuals = getIndividuals ( );
        if ( individualIds ):
            for index, id in enumerate ( individualIds ):
                individuals[index]["id"] = id;

        politicalParties = getPoliticalParties ( );
        if ( politicalPartyIDs ):
            for index, id in enumerate ( politicalPartyIDs ):
                politicalParties[index]["id"] = id;

        participants = individuals + politicalParties;

        assert areEqual ( participants, receivedParticipants ), f"Invalid response, expected {participants}, received {receivedParticipants}";

        setIndividualsAdded ( True );
        setPoliticalPartiesAdded ( True );

    return getParticipantsRequestTestImplementation;


def runParticipantTests ( adminAddress, withAuthentication, authenticationAddress, individualIds, politicalPartyIds ):

    tests = [
            # create participant authorization error
            ["post", "/createParticipant", setUpAuthorizationErrorRequest ( withAuthentication )         , { }, { }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],
            ["post", "/createParticipant", setUpUserHeaders ( withAuthentication, authenticationAddress ), { }, { }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],

            # create participant error
            ["post", "/createParticipant", setUpAdminHeaders ( withAuthentication, authenticationAddress ), { }, {             }, { }, 400, { "message": "Field name is missing."       }, equals, 1],
            ["post", "/createParticipant", setUpAdminHeaders ( withAuthentication, authenticationAddress ), { }, { "name": ""  }, { }, 400, { "message": "Field name is missing."       }, equals, 1],
            ["post", "/createParticipant", setUpAdminHeaders ( withAuthentication, authenticationAddress ), { }, { "name": " " }, { }, 400, { "message": "Field individual is missing." }, equals, 1],

            # get participant authorization error
            ["get", "/getParticipants", setUpAuthorizationErrorRequest ( withAuthentication )         , { }, { }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],
            ["get", "/getParticipants", setUpUserHeaders ( withAuthentication, authenticationAddress ), { }, { }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],

            # create participants
            *[
                    ["post", "/createParticipant", setUpCreateParticipantRequest ( withAuthentication, authenticationAddress, index, getIndividuals ), { }, { }, { }, 200, { }, createParticipantRequestTest ( index, getIndividuals ), 1]
                    for index, participant in enumerate ( getIndividuals ( ) )
            ],

            *[
                     ["post", "/createParticipant", setUpCreateParticipantRequest ( withAuthentication, authenticationAddress, index, getPoliticalParties ), { }, { }, { }, 200, { }, createParticipantRequestTest ( index, getPoliticalParties ), 1]
                     for index, participant in enumerate ( getPoliticalParties ( ) )
             ],

            # get participants
            ["get", "/getParticipants", setUpAdminHeaders ( withAuthentication, authenticationAddress ), { }, { }, { }, 200, { }, getParticipantsRequestTest ( individualIds, politicalPartyIds ), 4],
    ]

    for test in tests:
        test[1] = adminAddress + test[1];

    percentage = runTests ( tests );

    return percentage;
