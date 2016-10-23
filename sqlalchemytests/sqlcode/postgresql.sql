-- sudo -u postgres psql evalance
-- CREATE DATABASE evalance;
-- sudo -u postgres python learning.py

-- --------------------------------------------------------
-- Name: clean_tables
-- --------------------------------------------------------
DROP TABLE IF EXISTS memberships;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS teams;

-- --------------------------------------------------------
-- Name: scheme_definition
-- --------------------------------------------------------
CREATE TABLE users(
    user_id         SERIAL PRIMARY KEY,
    password_hash   VARCHAR(40) NOT NULL,
    first_name      VARCHAR(15) NOT NULL,
    mid_name        VARCHAR(15) NOT NULL,
    last_name       VARCHAR(30) NOT NULL,
    age             SMALLINT
                    CHECK(age >= 1 AND age < 150),
    last_logged     DATE NOT NULL default CURRENT_DATE
);

CREATE TABLE teams(
    team_id         SERIAL PRIMARY KEY,
    team_name       VARCHAR(40) UNIQUE NOT NULL -- Could be primary key :D
);

CREATE TABLE memberships(
    team_id         INTEGER REFERENCES teams(team_id),
    user_id         INTEGER REFERENCES users(user_id),
                    PRIMARY KEY (team_id, user_id),
    role            VARCHAR(30),
    cost            REAL
);

-- --------------------------------------------------------
-- Name: user_insertion
-- --------------------------------------------------------
INSERT INTO users (password_hash, first_name, mid_name, last_name, age)
VALUES ('%s', '%s', '%s', '%s', %d);

-- --------------------------------------------------------
-- Name: team_insertion
-- --------------------------------------------------------
INSERT INTO teams (team_name)
VALUES ('%s');

-- --------------------------------------------------------
-- Name: membership_insertion
-- --------------------------------------------------------
INSERT INTO memberships (team_id, user_id, role, cost)
VALUES (%d, %d, '%s', %f);

-- --------------------------------------------------------
-- Name: users_not_in_group
-- Gets all users not in a team (user id)
-- --------------------------------------------------------
SELECT users.user_id -- , memberships.team_id -> we can add this one to check that they are really nulls
FROM users
    LEFT JOIN  memberships
    ON memberships.user_id = users.user_id
WHERE memberships.team_id IS NULL;

-- --------------------------------------------------------
-- Name: Team cost
-- Calculates the total cost of each team (team name, cost)
-- --------------------------------------------------------
SELECT teams.team_id,teams.team_name, AVG(memberships.cost) as avg_cost
FROM users
    JOIN memberships
    ON memberships.user_id = users.user_id
    JOIN teams
    ON memberships.team_id = teams.team_id
GROUP BY teams.team_id
HAVING AVG(memberships.cost) > 500.
ORDER BY avg_cost ASC;

-- --------------------------------------------------------
-- Name: work_in_progress
-- Work in progress (in Join and ...)
-- --------------------------------------------------------
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
# Get the memberships with costs with exactly 2
# floating point positions
#---------------------------------------------------
