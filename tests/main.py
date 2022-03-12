import argparse;

from authenticationTests import runAuthenticationTests;
from electionTests       import runElectionTests;
from participantTests    import runParticipantTests;
from voteTests           import runVoteTests;

DELIMITER = "=" * 30;

parser = argparse.ArgumentParser ( description = "IEP project grading tests.", formatter_class = argparse.RawTextHelpFormatter );

parser.add_argument (
        "--authentication-address",
        help = "Address of the authentication container."
);

parser.add_argument (
        "--jwt-secret",
        help = "JWT secret used to encode JWT tokens."
);

parser.add_argument (
        "--roles-field",
        help = "Name of the field used to store role information in JWT token."
);

parser.add_argument (
        "--user-role",
        help = "Value which represents the user role."
);

parser.add_argument (
        "--administrator-role",
        help = "Value which represents the administrator role."
);

parser.add_argument (
        "--administrator-address",
        help = "Address of the administrator container."
);

parser.add_argument (
        "--with-authentication",
        action = "store_true",
        help = "Value which indicates if requests should include authorization header."
);

parser.add_argument (
        "--individual-ids",
        nargs = 3,
        type  = int,
        help  = "IDs of individual participants (exactly 3), if specified creation of individual participants will be skipped in tests."
);

parser.add_argument (
        "--political-party-ids",
        nargs = 5,
        type  = int,
        help  = "IDs of political parties (exactly 5), if specified creation of political parties will be skipped in tests."
);

parser.add_argument (
        "--station-address",
        help = "Address of the station container."
);

parser.add_argument (
        "--presidential-election-id",
        type = int,
        help = "ID of a presidential election that is already stored in the database."
);

parser.add_argument (
        "--presidential-election-start",
        help = "ISO string representing the start of a presidential election that is already stored in the database."
);

parser.add_argument (
        "--presidential-election-end",
        help = "ISO string representing the end of a presidential election that is already stored in the database."
);

parser.add_argument (
        "--parliamentary-election-id",
        type = int,
        help = "ID of a parliamentary election that is already stored in the database."
);

parser.add_argument (
        "--parliamentary-election-start",
        help = "ISO string representing the start of a parliamentary election that is already stored in the database."
);

parser.add_argument (
        "--parliamentary-election-end",
        help = "ISO string representing the end of a parliamentary election that is already stored in the database."
);

parser.add_argument (
        "--election-official-jmbg",
        help = "String representing the JMBG of the election official."
);

parser.add_argument (
        "--type",
        required = True,
        choices = ["authentication", "participant", "election", "vote", "without-authentication", "all"],
        default = "all",
        help = "Specifies which tests will be run. Each scenario requires a different set of parameters. Before running each scenario ensure that an admin user is stored in the database. Following scenarios are supported:\n" \
               "1) Value \"all\" is used for running all tests. Following parameters are required:\n" \
               "\t--authentication-address\n" \
               "\t--jwt-secret\n" \
               "\t--roles-field\n" \
               "\t--user-role\n" \
               "\t--admin-role\n" \
               "\t--administrator-address\n" \
               "\t--station-address\n" \
               "\t--with-authentication \n\n"
               "\tExample:\n" \
               "\tpython main.py --type all --authentication-address http://127.0.0.1:5000 --jwt-secret JWTSecretDevKey --roles-field roles --administrator-role administrator --user-role user --administrator-address http://127.0.0.1:5001 --station-address http://127.0.0.1:5002 --with-authentication\n\n" \
               "2) Value \"without-authentication\" is used for running all tests except the ones regarding authentication container. Following parameters are required:\n" \
               "\t--authentication-address\n" \
               "\t--jwt-secret\n" \
               "\t--roles-field\n" \
               "\t--user-role\n" \
               "\t--admin-role\n\n" \
               "\tExample:\n" \
               "\tpython main.py --type without-authentication --administrator-address http://127.0.0.1:5001 --station-address http://127.0.0.1:5002\n\n" \
               "3) Value \"participants\" is used for running tests which grade endpoints that create and retrieve participants. For these tests you can specify the following parameters:\n" \
               "\t--administrator-address\n" \
               "\t--with-authentication (if this is not present the penalty is 0.1 * score)\n" \
               "\t--authentication-address (if --with-authentication is present this argument is used to specify the address of the authentication container)\n" \
               "\t--individual-ids\n" \
               "\t--political-party-ids\n\n" \
               "\tTo test both endpoints or just the create endpoint you can use the following example command:\n" 
               "\tpython main.py --type participant --administrator-address http://127.0.0.1:5001 --with-authentication --authentication-address http://127.0.0.1:5000\n\n"
               "\tTo test just the retrieve endpoint you can use the following example command. Numbers 571, 572 and 573 represent ids of existing individual participants and the numbers 574, 575, 576, 577 and 578 represent the ids of existing political parties.\n"
               "\tpython main.py --type participant --administrator-address http://127.0.0.1:5001 --with-authentication --authentication-address http://127.0.0.1:5000 --individual-ids 571 572 573 --political-party-ids 574 575 576 577 578\n\n"
               "4) Value \"election\" is used for running the tests which grade endpoints that create and retrieve elections. For these tests you can specify the following parameters:\n" \
               "\t--administrator-address\n" \
               "\t--with-authentication (if this is not present the penalty is 0.1 * score)\n" \
               "\t--authentication-address (if --with-authentication is present this argument is used to specify the address of the authentication container)\n" \
               "\t--individual-ids\n" \
               "\t--political-party-ids\n" \
               "\t--presidential-election-start\n" \
               "\t--presidential-election-end\n" \
               "\t--parliamentary-election-start\n" \
               "\t--parliamentary-election-end\n\n" \
               "\tTo test both endpoints or just the create endpoint you can use the following example command:\n"
               "\tpython main.py --type election --administrator-address http://127.0.0.1:5001 --with-authentication --authentication-address http://127.0.0.1:5000\n\n"
               "\tThe tests rely on endpoints for creating and retrieving participants. However, if these are not implemented you can manually add participants in the database and use the following example command to run the tests. Numbers 595, 596 and 597 represent the ids of individual participants and the numbers 598, 599, 600, 601 and 602 represent the ids of political parties.\n"
               "\tpython main.py --type election --administrator-address http://127.0.0.1:5001 --with-authentication --authentication-address http://127.0.0.1:5000 --individual-ids 595 596 597 --political-party-ids 598 599 600 601 602\n\n"
               "\tTo test just the retrieve endpoint you can use the following command:\n"
               "\tpython main.py --type election --administrator-address http://127.0.0.1:5001 --with-authentication --authentication-address http://127.0.0.1:5000 --individual-ids 595 596 597 --political-party-ids 598 599 600 601 602 --presidential-election-start 2021-07-04T15:38:53 --presidential-election-end 2021-07-04T15:39:23 --parliamentary-election-start 2021-07-04T15:39:24 --parliamentary-election-end  2021-07-04T15:39:54\n\n"
               "5) Value \"vote\" is used for running tests which grade endpoints for voting and retrieving election results. For these tests you can specify the following parameters:\n" \
               "\t--administrator-address\n" \
               "\t--station-address\n" \
               "\t--with-authentication (if this is not present the penalty is 0.1 * score)\n" \
               "\t--authentication-address (if --with-authentication is present this argument is used to specify the address of the authentication container)\n" \
               "\t--presidential-election-id\n" \
               "\t--presidential-election-start\n" \
               "\t--presidential-election-end\n" \
               "\t--parliamentary-election-id\n" \
               "\t--parliamentary-election-start\n" \
               "\t--parliamentary-election-end\n\n" \
               "\tTo test both endpoints you can use the following example command:\n"
               "\tpython main.py --type vote --administrator-address http://127.0.0.1:5001 --station-address http://127.0.0.1:5002 --with-authentication --authentication-address http://127.0.0.1:5000\n\n"
               "\tThe tests rely on endpoints for creating and retrieving participants and elections. However, if these are not implemented you can manually add elections in the database and use the following example command to run the tests:\n"
               "\tpython main.py --type vote --administrator-address http://127.0.0.1:5001 --station-address http://127.0.0.1:5002 --with-authentication --authentication-address http://127.0.0.1:5000 --presidential-election-id 92 --presidential-election-start 2021-07-04T16:10:00 --presidential-election-end 2021-07-04T16:10:30 --parliamentary-election-id 93 --parliamentary-election-start 2021-07-04T16:11:00 --parliamentary-election-end  2021-07-04T16:11:30\n\n"
);


def checkArguments ( arguments, *keys ):
    present = True;
    for key in keys:
        if (key not in arguments):
            print ( f"Argument {key} is missing." )

    return present;


AUTHENTICATION = 20.;
PARTICIPANT    = 12.;
ELECTION       = 12.;
VOTE           = 16.;

AUTHENTICATION_FACTOR = 0.9;

if (__name__ == "__main__"):
    arguments = parser.parse_args ( );

    total = 0;
    max = 0;

    if ((arguments.type == "all") or (arguments.type == "authentication")):
        correct = checkArguments ( vars ( arguments ), "authentication_address", "jwt_secret", "roles_field", "user_role", "administrator_role" );
        if (correct):
            print ( "RUNNING AUTHENTICATION TESTS" );
            print ( DELIMITER );

            percentage = runAuthenticationTests (
                    arguments.authentication_address,
                    arguments.jwt_secret,
                    arguments.roles_field,
                    arguments.user_role,
                    arguments.administrator_role
            );

            authenticationScore = AUTHENTICATION * percentage;

            total += authenticationScore;
            max   += AUTHENTICATION;

            print ( f"AUTHENTICATION = {authenticationScore} / {AUTHENTICATION}" );
            print ( DELIMITER );

    if ((arguments.type == "all") or (arguments.type == "without-authentication") or (arguments.type == "participant")):
        correct = checkArguments ( vars ( arguments ), "administrator_address" );
        if (arguments.with_authentication):
            correct = checkArguments ( vars ( arguments ), "authentication_address" );

        if (correct):
            print ( "RUNNING PARTICIPANT TESTS" );
            print ( DELIMITER );

            percentage = runParticipantTests (
                    arguments.administrator_address,
                    arguments.with_authentication,
                    arguments.authentication_address,
                    arguments.individual_ids,
                    arguments.political_party_ids
            );

            participantScore = PARTICIPANT * percentage;

            if (not arguments.with_authentication):
                participantScore *= AUTHENTICATION_FACTOR;

            total += participantScore;
            max   += PARTICIPANT;

            print ( f"PARTICIPANTS = {participantScore} / {PARTICIPANT}" );
            print ( DELIMITER );

    if ((arguments.type == "all") or (arguments.type == "without-authentication") or (arguments.type == "election")):
        correct = checkArguments ( vars ( arguments ), "administrator_address" );
        if (arguments.with_authentication):
            correct = checkArguments ( vars ( arguments ), "authentication_address" );

        if (correct):
            print ( "RUNNING ELECTION TESTS" );
            print ( DELIMITER );

            percentage = runElectionTests (
                    arguments.administrator_address,
                    arguments.with_authentication,
                    arguments.authentication_address,
                    arguments.individual_ids,
                    arguments.political_party_ids,
                    arguments.presidential_election_start,
                    arguments.presidential_election_end,
                    arguments.parliamentary_election_start,
                    arguments.parliamentary_election_end,
            );

            electionScore = ELECTION * percentage;

            if (not arguments.with_authentication):
                electionScore *= AUTHENTICATION_FACTOR;

            total += electionScore;
            max   += ELECTION;

            print ( f"ELECTION = {electionScore} / {ELECTION}" );
            print ( DELIMITER );

    if ((arguments.type == "all") or (arguments.type == "without-authentication") or (arguments.type == "vote")):
        correct = checkArguments ( vars ( arguments ), "administrator_address", "station_address" );
        if (arguments.with_authentication):
            correct = checkArguments ( vars ( arguments ), "authentication_address" );

        if (correct):
            print ( "RUNNING VOTE TESTS" );
            print ( DELIMITER );

            percentage = runVoteTests (
                    arguments.administrator_address,
                    arguments.station_address,
                    arguments.with_authentication,
                    arguments.authentication_address,
                    arguments.presidential_election_id,
                    arguments.presidential_election_start,
                    arguments.presidential_election_end,
                    arguments.parliamentary_election_id,
                    arguments.parliamentary_election_start,
                    arguments.parliamentary_election_end,
                    arguments.election_official_jmbg
            );

            voteScore = VOTE * percentage;

            if (not arguments.with_authentication):
                voteScore *= AUTHENTICATION_FACTOR;

            total += voteScore;
            max   += VOTE;

            print ( f"VOTE = {voteScore} / {VOTE}" );
            print ( DELIMITER );

    print ( f"SCORE = {total} / {max}" );
