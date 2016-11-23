#sudo -u postgres psql evalance
#CREATE DATABASE evalance;
#sudo -u postgres python postgre_main.py

import unittest
import sqlalchemytests.sqlcode
from sqlalchemytests.tools.data_gneration import gen_users, get_team_names, gen_memberships
from sqlalchemytests.tools.sql_files import parse_sql_file, get_transaction_set
from sqlalchemytests.tools.transactions import open_connection, run_transactions
from sqlalchemytests.sqlcode.alchemy import alchemy_functions


def test_alchemy(test_case_name):
    """
    Uses unittest functions to assess that the results from the raw SQL query are equal
    to the ones got with SQLAlchemy.

    :param test_case_name: The string describing an SQL query name and a function containing
    the SQLAlchemy code needed to obtain the same results.
    """
    #tc = unittest.TestCase()
    result = run_transactions(connection, get_transaction_set(test_case_name, parsed_file))
    result_alch = alchemy_functions[test_case_name]()
    print [row for row in result]
    print [row for row in result_alch]
    try:
        unittest.TestCase__assertItemsEqual([row for row in result], [row for row in result_alch])
    except:
        print "{} failed.".format(test_case_name)

if __name__ == '__main__':
    parsed_file = parse_sql_file(open(sqlalchemytests.sqlcode.files["postgre"]))

    connection = open_connection('postgresql:///evalance')

    run_transactions(connection, get_transaction_set("clean_tables", parsed_file))
    run_transactions(connection, get_transaction_set("scheme_definition", parsed_file))

    NUM_USERS = 150
    users = gen_users(NUM_USERS)
    user_insertion_template = get_transaction_set("user_insertion_template", parsed_file).pop()
    all_user_transactions = [user_insertion_template.format(**user) for user in users]
    run_transactions(connection, all_user_transactions)

    NUM_TEAMS = 30
    team_names = get_team_names(NUM_TEAMS)
    team_insertion_template = get_transaction_set("team_insertion_template", parsed_file).pop()
    all_team_transactions = [team_insertion_template.format(team_name=s) for s in team_names]
    run_transactions(connection, all_team_transactions)

    MAX_MEMBERSHIPS = 100
    NUM_ROLES = 10
    memberships = gen_memberships(NUM_USERS, NUM_TEAMS, NUM_ROLES, MAX_MEMBERSHIPS)
    membership_insertion_template = get_transaction_set("membership_insertion_template", parsed_file).pop()
    all_membership_transactions = [membership_insertion_template.format(**memb) for memb in memberships]
    run_transactions(connection, all_membership_transactions)

    test_alchemy("users_not_in_group")
    test_alchemy("team_cost")

    connection.close()
