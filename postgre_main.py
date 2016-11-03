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

# #----------------------------------------
# # Get all users not in a group (user id)
# #----------------------------------------
#
# trans = connection.begin()
# try:
#     results = connection.execute("""
# SELECT users.user_id-- , memberships.team_id -> we can add this one to check that they are really nulls
# FROM users
#     LEFT JOIN  memberships
#     ON memberships.user_id = users.user_id
# WHERE memberships.team_id IS NULL;""")
#     #for row in results: print row
#     trans.commit()
# except:
#     trans.rollback()
#     raise
#
# #---------------------------------------------------
# # Get the total cost of each team (team name, cost)
# #---------------------------------------------------
#
# trans = connection.begin()
# try:
#     results = connection.execute("""
# SELECT teams.team_id,teams.team_name, AVG(memberships.cost) as avg_cost
# FROM users
#     JOIN memberships
#     ON memberships.user_id = users.user_id
#     JOIN teams
#     ON memberships.team_id = teams.team_id
# GROUP BY teams.team_id
# HAVING AVG(memberships.cost) > 500.
# ORDER BY avg_cost ASC;""")
#     #for row in results: print row
#     trans.commit()
# except:
#     trans.rollback()
#     raise
#
# #---------------------------
# # Nested subqueries (in Join and ...)
# #---------------------------
#
# #---------------------------
# # And the same with a view
# #---------------------------
#
# #---------------------------------------------------
# # Get the memberships with costs with 2 or less
# # floating point positions
# #---------------------------------------------------
# CREATE FUNCTION SUPER_ROUND(NUMERIC, INTEGER) RETURNS NUMERIC AS
# $function$
#     SELECT ROUND(CAST(ROUND(CAST($1 AS NUMERIC),$2)*POW(10,$2) - FLOOR($1)*POW(10,$2) AS NUMERIC),$2);
# $function$
# LANGUAGE SQL;
#
# CREATE FUNCTION REMAINING_DECIMAL(NUMERIC, INTEGER) RETURNS NUMERIC AS
# $function$
#     SELECT SUPER_ROUND($1, $2) - FLOOR(SUPER_ROUND($1, $2));
# $function$
# LANGUAGE SQL;
#
# SELECT users.user_id, memberships.cost, REMAINING_DECIMAL(CAST(memberships.cost AS NUMERIC),2)
# FROM users
# JOIN memberships
# ON memberships.user_id = users.user_id
# WHERE REMAINING_DECIMAL(CAST(memberships.cost AS NUMERIC),2) <> 0;
#
# #---------------------------------------------------
# # Get the memberships with costs with exxactly 2
# # floating point positions
# #---------------------------------------------------
#
#
# # stored procedures, try to have always updated a table with the number of users logged per day
# # new transction, BEGIN issued
# #result = connection.execute("select username from users")
# # ended transaction, COMMIT issued
# connection.close()
#
#
