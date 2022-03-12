import sys;

from datetime  import datetime;
from jwt       import decode;
from requests  import request;
from data      import getUser;
from data      import setUserRegistered;
from utilities import equals;
from utilities import setUpPassFunction;
from utilities import setUpAdminHeaders;
from utilities import setUpUserHeaders;
from utilities import runTests;


def userRegisterEquals ( setUpData, expectedResponse, receivedResponse ):
    equals ( setUpData, expectedResponse, receivedResponse );
    setUserRegistered ( True );

def tokenTest ( response, user, tokenField, secret, expectedType, expectedSubject, expectedForename, expectedSurname, expectedJmbg, rolesField, expectedRole, expectedExpiresDelta ):
    assert tokenField in response, f"Login response error, {tokenField} field missing for user {user}.";

    token = decode ( response[tokenField], key = secret, algorithms = ["HS256"] );

    assert "nbf"      in token, f"{tokenField} error for user {user}, field nbf is missing."
    assert "type"     in token, f"{tokenField} error for user {user}, field type is missing."
    assert "exp"      in token, f"{tokenField} error for user {user}, field exp is missing."
    assert "sub"      in token, f"{tokenField} error for user {user}, field sub is missing."
    assert "forename" in token, f"{tokenField} error for user {user}, field forename is missing."
    assert "surname"  in token, f"{tokenField} error for user {user}, field surname is missing."
    assert "jmbg"     in token, f"{tokenField} error for user {user}, field jmbg is missing."
    assert rolesField in token, f"{tokenField} error for user {user}, field {rolesField} is missing."

    nbf      = token["nbf"]
    type     = token["type"]
    exp      = token["exp"]
    sub      = token["sub"]
    forename = token["forename"]
    surname  = token["surname"]
    jmbg     = token["jmbg"]
    roles    = token[rolesField]

    assert type     == expectedType                            , f"{tokenField} error for user {user}, field type has an incorrect value, expected {expectedType}, got {type}."
    assert sub      == expectedSubject                         , f"{tokenField} error for user {user}, field sub has an incorrect value, expected {expectedSubject}, got {sub}."
    assert forename == expectedForename                        , f"{tokenField} error for user {user}, field forename has an incorrect value, expected {expectedForename}, got {forename}."
    assert surname  == expectedSurname                         , f"{tokenField} error for user {user}, field surname has an incorrect value, expected {expectedSurname}, got {surname}."
    assert jmbg     == expectedJmbg                            , f"{tokenField} error for user {user}, field jmbg has an incorrect value, expected {expectedJmbg}, got {jmbg}."
    assert (roles   == expectedRole) or (expectedRole in roles), f"{tokenField} error for user {user}, field {rolesField} has an incorrect value, expected {expectedRole}, got {roles}."

    expiresDelta = datetime.fromtimestamp ( exp ) - datetime.fromtimestamp ( nbf );

    assert expiresDelta.total_seconds ( ) == expectedExpiresDelta, f"{tokenField} error for user {user}, expiration has an incorrect value, expected {expectedExpiresDelta}, got {expiresDelta.total_seconds ( )}."

def setUpRefreshRequest ( authenticationAddress, headers, email, password ):
    loginData = {
            "email"   : email,
            "password": password,
    };

    response = request (
            method  = "post",
            url     = authenticationAddress + "/login",
            headers = { },
            json    = loginData
    );

    headers["Authorization"] = "Bearer " + response.json ( )["refreshToken"];

def adminTokenTest ( response, tokenField, secret, expectedType, rolesField, expectedRole, expectedExpiresDelta ):
    tokenTest (
            response             = response,
            user                 = "admin",
            tokenField           = tokenField,
            secret               = secret,
            expectedType         = expectedType,
            expectedSubject      = "admin@admin.com",
            expectedForename     = "admin",
            expectedSurname      = "admin",
            expectedJmbg         = "0000000000000",
            rolesField           = rolesField,
            expectedRole         = expectedRole,
            expectedExpiresDelta = expectedExpiresDelta
    );

def adminAccessTokenTestWrapper ( response, secret, rolesField, expectedRole ):
    adminTokenTest (
            response             = response,
            tokenField           = "accessToken",
            secret               = secret,
            expectedType         = "access",
            rolesField           = rolesField,
            expectedRole         = expectedRole,
            expectedExpiresDelta = 60 * 60
    );

def adminRefreshTokenTestWrapper ( response, secret, rolesField, expectedRole ):
    adminTokenTest (
            response             = response,
            tokenField           = "refreshToken",
            secret               = secret,
            expectedType         = "refresh",
            rolesField           = rolesField,
            expectedRole         = expectedRole,
            expectedExpiresDelta = 30 * 24 * 60 * 60
    );

def adminAccessTokenTest ( jwtSecret, rolesField, administratorRole ):
    def adminAccessTokenTestImplementation ( setUpData, expectedResponse, receivedResponse ):
        adminAccessTokenTestWrapper (
                response     = receivedResponse,
                secret       = jwtSecret,
                rolesField   = rolesField,
                expectedRole = administratorRole
        );

    return adminAccessTokenTestImplementation;

def adminRefreshTokenTest ( jwtSecret, rolesField, administratorRole ):
    def adminRefreshTokenTestImplementation ( setUpData, expectedResponse, receivedResponse ):
        adminRefreshTokenTestWrapper (
                response     = receivedResponse,
                secret       = jwtSecret,
                rolesField   = rolesField,
                expectedRole = administratorRole
        );

    return adminRefreshTokenTestImplementation;

def setUpAdminRefreshRequest ( authenticationAddress ):
    def setUpAdminRefreshRequestImplementation ( url, headers, data, files ):
        setUpRefreshRequest (
                authenticationAddress = authenticationAddress,
                headers               = headers,
                email                 = "admin@admin.com",
                password              = "1"
        );

        return (url, None, False);

    return setUpAdminRefreshRequestImplementation;

def userTokenTest ( response, tokenField, secret, expectedType, rolesField, expectedRole, expectedExpiresDelta ):
    tokenTest (
            response             = response,
            user                 = getUser ( )["forename"],
            tokenField           = tokenField,
            secret               = secret,
            expectedType         = expectedType,
            expectedSubject      = getUser ( )["email"],
            expectedForename     = getUser ( )["forename"],
            expectedSurname      = getUser ( )["surname"],
            expectedJmbg         = getUser ( )["jmbg"],
            rolesField           = rolesField,
            expectedRole         = expectedRole,
            expectedExpiresDelta = expectedExpiresDelta
    );

def userAccessTokenTestWrapper ( response, secret, rolesField, expectedRole ):
    userTokenTest (
            response             = response,
            tokenField           = "accessToken",
            secret               = secret,
            expectedType         = "access",
            rolesField           = rolesField,
            expectedRole         = expectedRole,
            expectedExpiresDelta = 60 * 60
    );

def userRefreshTokenTestWrapper ( response, secret, rolesField, expectedRole ):
    userTokenTest (
            response             = response,
            tokenField           = "refreshToken",
            secret               = secret,
            expectedType         = "refresh",
            rolesField           = rolesField,
            expectedRole         = expectedRole,
            expectedExpiresDelta = 30 * 24 * 60 * 60
    );

def userAccessTokenTest ( jwtSecret, rolesField, userRole ):
    def userAccessTokenTestImplementation ( setUpData, expectedResponse, receivedResponse ):
        userAccessTokenTestWrapper (
                response     = receivedResponse,
                secret       = jwtSecret,
                rolesField   = rolesField,
                expectedRole = userRole
        );

    return userAccessTokenTestImplementation;

def setUpUserRefreshRequest ( authenticationAddress ):
    def setUpUserRefreshRequestImplementation ( url, headers, data, files ):
        setUpRefreshRequest (
                authenticationAddress = authenticationAddress,
                headers               = headers,
                email                 = getUser ( )["email"],
                password              = getUser ( )["password"]
        );

        return (url, None, False);

    return setUpUserRefreshRequestImplementation;

def userRefreshTokenTest ( jwtSecret, rolesField, userRole ):
    def userRefreshTokenTestImplementation ( setUpData, expectedResponse, receivedResponse ):
        userRefreshTokenTestWrapper (
                response     = receivedResponse,
                secret       = jwtSecret,
                rolesField   = rolesField,
                expectedRole = userRole
        );

    return userRefreshTokenTestImplementation;

def userDeleteEquals ( setUpData, expectedResponse, receivedResponse ):
    equals ( setUpData, expectedResponse, receivedResponse );
    setUserRegistered ( False );


def runAuthenticationTests ( authenticationAddress, jwtSecret, rolesField, userRole, administratorRole ):
    tests = [
            # register errors
            ["post", "/register", setUpPassFunction, { }, {                                                                                                                    }, { }, 400, { "message": "Field jmbg is missing."     }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": ""                                                                                                         }, { }, 400, { "message": "Field jmbg is missing."     }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": " "                                                                                                        }, { }, 400, { "message": "Field forename is missing." }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": " "            , "forename": ""                                                                            }, { }, 400, { "message": "Field forename is missing." }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": " "            , "forename": " "                                                                           }, { }, 400, { "message": "Field surname is missing."  }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": " "            , "forename": " "   , "surname": ""                                                         }, { }, 400, { "message": "Field surname is missing."  }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": " "            , "forename": " "   , "surname": " "                                                        }, { }, 400, { "message": "Field email is missing."    }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": " "            , "forename": " "   , "surname": " "  , "email": ""                                         }, { }, 400, { "message": "Field email is missing."    }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": " "            , "forename": " "   , "surname": " "  , "email": " "                                        }, { }, 400, { "message": "Field password is missing." }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": " "            , "forename": " "   , "surname": " "  , "email": " "              , "password": ""          }, { }, 400, { "message": "Field password is missing." }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": " "            , "forename": " "   , "surname": " "  , "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid jmbg."              }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0000000000000", "forename": " "   , "surname": " "  , "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid jmbg."              }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "3200000000000", "forename": " "   , "surname": " "  , "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid jmbg."              }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0100000000000", "forename": " "   , "surname": " "  , "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid jmbg."              }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0113000000000", "forename": " "   , "surname": " "  , "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid jmbg."              }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101000000000", "forename": " "   , "surname": " "  , "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid jmbg."              }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994000000", "forename": " "   , "surname": " "  , "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid jmbg."              }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994000000", "forename": " "   , "surname": " "  , "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid jmbg."              }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994700000", "forename": " "   , "surname": " "  , "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid jmbg."              }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704400", "forename": " "   , "surname": " "  , "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid jmbg."              }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": " "              , "password": " "         }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": "john"           , "password": " "         }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": "john@"          , "password": " "         }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": "john@gmail"     , "password": " "         }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": "john@gmail."    , "password": " "         }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": "john@gmail.a"   , "password": " "         }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": "john@gmail.com" , "password": " "         }, { }, 400, { "message": "Invalid password."          }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": "john@gmail.com" , "password": "aaaaaaaa"  }, { }, 400, { "message": "Invalid password."          }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": "john@gmail.com" , "password": "aaaaaaaaa" }, { }, 400, { "message": "Invalid password."          }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": "john@gmail.com" , "password": "Aaaaaaaaa" }, { }, 400, { "message": "Invalid password."          }, equals, 1],
            ["post", "/register", setUpPassFunction, { }, { "jmbg": "0101994704401", "forename": "John", "surname": "Doe", "email": "admin@admin.com", "password": "Aaaaaaaa1" }, { }, 400, { "message": "Email already exists."      }, equals, 1],

            # login errors
            ["post", "/login", setUpPassFunction, { }, {                                              }, { }, 400, { "message": "Field email is missing."    }, equals, 1],
            ["post", "/login", setUpPassFunction, { }, { "email": ""                                  }, { }, 400, { "message": "Field email is missing."    }, equals, 1],
            ["post", "/login", setUpPassFunction, { }, { "email": " "                                 }, { }, 400, { "message": "Field password is missing." }, equals, 1],
            ["post", "/login", setUpPassFunction, { }, { "email": " "             , "password": ""    }, { }, 400, { "message": "Field password is missing." }, equals, 1],
            ["post", "/login", setUpPassFunction, { }, { "email": "john"          , "password": " "   }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/login", setUpPassFunction, { }, { "email": "john@"         , "password": " "   }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/login", setUpPassFunction, { }, { "email": "john@gmail"    , "password": " "   }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/login", setUpPassFunction, { }, { "email": "john@gmail."   , "password": " "   }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/login", setUpPassFunction, { }, { "email": "john@gmail.a"  , "password": " "   }, { }, 400, { "message": "Invalid email."             }, equals, 1],
            ["post", "/login", setUpPassFunction, { }, { "email": "john@gmail.com", "password": "123" }, { }, 400, { "message": "Invalid credentials."       }, equals, 1],

            # refresh errors
            ["post", "/refresh", setUpPassFunction, { }, { }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],

            # delete errors
            ["post", "/delete", setUpPassFunction                                , { }, {                           }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],
            ["post", "/delete", setUpAdminHeaders ( True, authenticationAddress ), { }, {                           }, { }, 400, { "message": "Field email is missing."  }, equals, 1],
            ["post", "/delete", setUpAdminHeaders ( True, authenticationAddress ), { }, { "email": ""               }, { }, 400, { "message": "Field email is missing."  }, equals, 1],
            ["post", "/delete", setUpAdminHeaders ( True, authenticationAddress ), { }, { "email": "john@"          }, { }, 400, { "message": "Invalid email."           }, equals, 1],
            ["post", "/delete", setUpAdminHeaders ( True, authenticationAddress ), { }, { "email": "john@gmail"     }, { }, 400, { "message": "Invalid email."           }, equals, 1],
            ["post", "/delete", setUpAdminHeaders ( True, authenticationAddress ), { }, { "email": "john@gmail."    }, { }, 400, { "message": "Invalid email."           }, equals, 1],
            ["post", "/delete", setUpAdminHeaders ( True, authenticationAddress ), { }, { "email": "john@gmail.a"   }, { }, 400, { "message": "Invalid email."           }, equals, 1],
            ["post", "/delete", setUpAdminHeaders ( True, authenticationAddress ), { }, { "email": "john@gmail.a"   }, { }, 400, { "message": "Invalid email."           }, equals, 1],
            ["post", "/delete", setUpAdminHeaders ( True, authenticationAddress ), { }, { "email": "john@gmail.com" }, { }, 400, { "message": "Unknown user."            }, equals, 1],
            ["post", "/delete", setUpUserHeaders ( True, authenticationAddress ) , { }, {                           }, { }, 401, { "msg": "Missing Authorization Header" }, equals, 1],

            # user delete
            ["post", "/delete", setUpAdminHeaders ( True, authenticationAddress ), { }, { "email": getUser ( ) ["email"] }, { }, 200, None, userDeleteEquals, 7],
            ["post", "/login", setUpPassFunction, { }, { "email": getUser ( ) ["email"], "password": getUser ( ) ["password"] }, { }, 400, { "message": "Invalid credentials." }, equals, 2],

            # admin login
            ["post", "/login", setUpPassFunction, { }, { "email": "admin@admin.com", "password": "1" }, { }, 200, { }, adminAccessTokenTest ( jwtSecret, rolesField, administratorRole ) , 2],
            ["post", "/login", setUpPassFunction, { }, { "email": "admin@admin.com", "password": "1" }, { }, 200, { }, adminRefreshTokenTest ( jwtSecret, rolesField, administratorRole ), 2],

            # user register
            ["post", "/register", setUpPassFunction, { }, getUser ( ), { }, 200, None, userRegisterEquals, 10],

            # user login
            ["post", "/login", setUpPassFunction, { }, { "email": getUser ( ) ["email"], "password": getUser ( ) ["password"] }, { }, 200, { }, userAccessTokenTest ( jwtSecret, rolesField, userRole ) , 2],
            ["post", "/login", setUpPassFunction, { }, { "email": getUser ( ) ["email"], "password": getUser ( ) ["password"] }, { }, 200, { }, userRefreshTokenTest ( jwtSecret, rolesField, userRole ), 2],

            # admin refresh
            ["post", "/refresh", setUpAdminRefreshRequest ( authenticationAddress ), { }, { }, { }, 200, { }, adminAccessTokenTest ( jwtSecret, rolesField, administratorRole ), 1],

            # user refresh
            ["post", "/refresh", setUpUserRefreshRequest ( authenticationAddress ), { }, { }, { }, 200, { }, userAccessTokenTest ( jwtSecret, rolesField, userRole ), 1],
    ];

    for test in tests:
        test[1] = authenticationAddress + test[1];

    percentage = runTests ( tests );

    return percentage;