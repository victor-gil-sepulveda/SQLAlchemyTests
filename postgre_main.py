#sudo -u postgres psql evalance
#CREATE DATABASE evalance;
#sudo -u postgres python learning.py
import math
import random

from sqlalchemytests.tools.sql_files import parse_sql_file
from sqlalchemytests.tools.transactions import open_connection

if __name__ == '__main__':
    parse_sql_file()

    connection = open_connection('postgresql:///evalance')


from sqlalchemy import create_engine
engine = create_engine('postgresql:///evalance')

connection = engine.connect()

trans = connection.begin()
try:
    connection.execute("DROP TABLE IF EXISTS memberships;")
    connection.execute("DROP TABLE IF EXISTS users;")
    connection.execute("DROP TABLE IF EXISTS teams;")
    trans.commit()
except:
    trans.rollback()
    raise


trans = connection.begin()
# As PostgreSQL DDL is transactional we can create the tables within a transaction
try:
    connection.execute("""
CREATE TABLE users(
    user_id         SERIAL PRIMARY KEY,
    password_hash   VARCHAR(40) NOT NULL,
    first_name      VARCHAR(15) NOT NULL,
    mid_name        VARCHAR(15) NOT NULL,
    last_name       VARCHAR(30) NOT NULL,
    age             SMALLINT
                    CHECK(age >= 1 AND age < 150),
    last_logged     DATE NOT NULL default CURRENT_DATE
);""")

    connection.execute("""
CREATE TABLE teams(
    team_id         SERIAL PRIMARY KEY,
    team_name       VARCHAR(40) UNIQUE NOT NULL -- Could be primary key :D
);""")

    connection.execute("""
CREATE TABLE memberships(
    team_id         INTEGER REFERENCES teams(team_id),
    user_id         INTEGER REFERENCES users(user_id),
                    PRIMARY KEY (team_id, user_id),
    role            VARCHAR(30),
    cost            REAL
);""")
        
    trans.commit()
except:
    trans.rollback()
    raise

#----------------------------
NUM_USERS = 100
first_names, mid_names, last_names = gen_names(NUM_USERS)
ages = [(100*random.random())+1 for i in range(NUM_USERS)]
import string
password_hashes = ["".join([random.choice(string.ascii_lowercase+string.ascii_uppercase) for _ in range(10)]) for _ in range(len(first_names))]

trans = connection.begin()
try:
    for i in range(NUM_USERS):
        connection.execute("""
INSERT INTO users (password_hash, first_name, mid_name, last_name, age)
VALUES ('%s', '%s', '%s', '%s', %d);"""%(password_hashes[i], first_names[i], mid_names[i], last_names[i], ages[i]))
    
    trans.commit()
except:
    trans.rollback()
    raise
#----------------------------

team_names = [line.strip() for line in open("team_names.txt")]
NUM_TEAMS = 35

trans = connection.begin()
try:
    random.shuffle(team_names)
    for i in range(NUM_TEAMS):
        connection.execute("""
INSERT INTO teams (team_name)
VALUES ('%s');"""%(team_names[i]))
    
    trans.commit()
except:
    trans.rollback()
    raise
#-----------------------------
roles = list(set( [line.strip().split()[0].replace("'","") for line in open("professions.txt")]))
#choose people and teams randomly
MAX_MEMBERSHIPS = 50
memberships = list(set([(1+random.choice(range(NUM_USERS)),1+random.choice(range(NUM_TEAMS))) for i in range(MAX_MEMBERSHIPS)]))
trans = connection.begin()
costs = [float("%d.%d"%(math.floor(random.random()*1000),math.floor(random.random()*(10**math.ceil(random.random()*4))))) for i in range(MAX_MEMBERSHIPS)] 
print costs
try:
    random.shuffle(team_names)
    for i in range(len(memberships)):
        connection.execute("""
INSERT INTO memberships (team_id, user_id, role, cost)
VALUES (%d, %d, '%s', %f);"""%(memberships[i][1], memberships[i][0], random.choice(roles), costs[i]))
    trans.commit()
except:
    trans.rollback()
    raise

#----------------------------------------
# Get all users not in a group (user id)
#----------------------------------------

trans = connection.begin()
try:
    results = connection.execute("""
SELECT users.user_id-- , memberships.team_id -> we can add this one to check that they are really nulls
FROM users
    LEFT JOIN  memberships
    ON memberships.user_id = users.user_id
WHERE memberships.team_id IS NULL;""")
    #for row in results: print row
    trans.commit()
except:
    trans.rollback()
    raise

#---------------------------------------------------
# Get the total cost of each team (team name, cost)
#---------------------------------------------------

trans = connection.begin()
try:
    results = connection.execute("""
SELECT teams.team_id,teams.team_name, AVG(memberships.cost) as avg_cost
FROM users
    JOIN memberships
    ON memberships.user_id = users.user_id
    JOIN teams
    ON memberships.team_id = teams.team_id
GROUP BY teams.team_id 
HAVING AVG(memberships.cost) > 500.
ORDER BY avg_cost ASC;""")
    #for row in results: print row
    trans.commit()
except:
    trans.rollback()
    raise

#---------------------------
# Nested subqueries (in Join and ...)
#---------------------------

#---------------------------
# And the same with a view
#---------------------------

#---------------------------------------------------
# Get the memberships with costs with 2 or less 
# floating point positions
#---------------------------------------------------
CREATE FUNCTION SUPER_ROUND(NUMERIC, INTEGER) RETURNS NUMERIC AS
$function$
    SELECT ROUND(CAST(ROUND(CAST($1 AS NUMERIC),$2)*POW(10,$2) - FLOOR($1)*POW(10,$2) AS NUMERIC),$2);
$function$
LANGUAGE SQL;

CREATE FUNCTION REMAINING_DECIMAL(NUMERIC, INTEGER) RETURNS NUMERIC AS
$function$
    SELECT SUPER_ROUND($1, $2) - FLOOR(SUPER_ROUND($1, $2));
$function$
LANGUAGE SQL;

SELECT users.user_id, memberships.cost, REMAINING_DECIMAL(CAST(memberships.cost AS NUMERIC),2)
FROM users
JOIN memberships 
ON memberships.user_id = users.user_id
WHERE REMAINING_DECIMAL(CAST(memberships.cost AS NUMERIC),2) <> 0;

#---------------------------------------------------
# Get the memberships with costs with exxactly 2  
# floating point positions
#---------------------------------------------------


# stored procedures, try to have always updated a table with the number of users logged per day
# new transction, BEGIN issued
#result = connection.execute("select username from users")
# ended transaction, COMMIT issued
connection.close()


