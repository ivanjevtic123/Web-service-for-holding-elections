from requests import request;
from copy     import deepcopy;
from data     import getUser;
from data     import getUserRegistered;
from data     import setUserRegistered;


def copyDictionary ( destination, source ):
    for key in source:
        destination [key] = deepcopy ( source [key] );


def areEqual ( list0, list1 ):
    difference = [item for item in (list0 + list1) if ((item not in list0) or (item not in list1))];

    return len ( difference ) == 0;


def setUpPassFunction ( url, headers, data, files ):
    return (url, None, False);


def setUpAuthorizationErrorRequest ( withAuthentication ):
    def setUpAuthorizationErrorRequestImplementation ( url, headers, data, files ):
        if (not withAuthentication):
            return (url, None, True);

        return (url, None, False);

    return setUpAuthorizationErrorRequestImplementation;


def adminLogin ( authenticationAddress, headers ):
    response = request (
            method  = "post",
            url     = authenticationAddress + "/login",
            headers = { },
            json    = {
                    "email"   : "admin@admin.com",
                    "password": "1"
            }
    );

    headers ["Authorization"] = "Bearer " + response.json ( ) ["accessToken"];


def setUpAdminHeaders ( withAuthentication, authenticationAddress ):
    def setUpAdminHeadersImplementation ( url, headers, data, files ):
        if (withAuthentication):
            adminLogin ( authenticationAddress, headers );
        return (url, None, False);

    return setUpAdminHeadersImplementation;


def userLogin ( authenticationAddress, headers ):
    if (not getUserRegistered ( )):
        response = request (
                method  = "post",
                url     = authenticationAddress + "/register",
                headers = { },
                json    = getUser ( )
        );
        setUserRegistered ( True );

    response = request (
            method  = "post",
            url     = authenticationAddress + "/login",
            headers = { },
            json    = {
                    "email"   : getUser ( ) ["email"],
                    "password": getUser ( ) ["password"]
            }
    );

    headers ["Authorization"] = "Bearer " + response.json ( ) ["accessToken"];


def setUpUserHeaders ( withAuthentication, authenticationAddress ):
    def setUpUserHeadersImplementation ( url, headers, data, files ):
        if (withAuthentication):
            userLogin ( authenticationAddress, headers );

        return (url, "", False);

    return setUpUserHeadersImplementation;


def equals ( setUpData, expectedResponse, receivedResponse ):
    assert expectedResponse == receivedResponse, f"Invalid response, expected {expectedResponse}, received {receivedResponse}.";


def addParticipants ( withAuthentication, authenticationAddress, administratorAddress, getParticipantsFunction, setParticipantsAddedFunction ):
    headers = { };
    if (withAuthentication):
        adminLogin ( authenticationAddress, headers );

    for index in range ( len ( getParticipantsFunction ( ) ) ):
        response = request (
                method  = "post",
                url     = administratorAddress + "/createParticipant",
                headers = headers,
                json    = getParticipantsFunction ( ) [index]
        );

        getParticipantsFunction ( ) [index] ["id"] = response.json ( ) ["id"];

    setParticipantsAddedFunction ( True );

def setParticipantIds ( getParticipantFunction, setParticipantsAddedFunction, ids ):
    for index, id in enumerate ( ids ):
        getParticipantFunction ( )[index]["id"] = id;

    setParticipantsAddedFunction ( True );


def setUpAddElectionData ( data, updateElectionTimeFunction, getElectionFunction, getParticipantsFunction ):
    updateElectionTimeFunction ( );
    copyDictionary ( data, getElectionFunction ( ) );

    pollNumbers = [ ];

    for index, participant in enumerate ( getParticipantsFunction ( ) ):

        data ["participants"].append ( participant ["id"] );

        getElectionFunction ( ) ["participants"].append ( {
                "id"  : participant ["id"],
                "name": participant ["name"]
        } );

        pollNumbers.append ( index + 1 );

    return pollNumbers;


def runTests ( tests ):
    max   = 0;
    total = 0;

    for index, test in enumerate ( tests ):
        method                 = test [0];
        url                    = test [1];
        preparationFunction    = test [2];
        headers                = test [3];
        data                   = test [4];
        files                  = test [5];
        expectedStatusCode     = test [6];
        expectedResponse       = test [7];
        testAndCleanupFunction = test [8];
        score                  = test [9];

        max   += score
        total += score;

        try:
            (url, setUpData, skipTest) = preparationFunction ( url, headers, data, files );

            if (not skipTest):
                response = request (
                        method  = method,
                        url     = url,
                        headers = headers,
                        json    = data,
                        files   = files
                );

                for key in files:
                    files [key].close ( );

                assert response.status_code == expectedStatusCode, f"Invalid status code, expected {expectedStatusCode}, received {response.status_code}";

                if (expectedResponse is not None):
                    receivedResponse = response.json ( );
                else:
                    expectedResponse = { };
                    receivedResponse = { };

                testAndCleanupFunction ( setUpData, expectedResponse, receivedResponse );

        except Exception as error:
            print ( f"Failed test number {index}\n\t method = {method}\n\t url = {url}\n\t headers = {headers}\n\t data = {data}\n\t files = {files}\n\t error: {error}" );
            total -= score;

    return total / max if (max != 0) else 0;
