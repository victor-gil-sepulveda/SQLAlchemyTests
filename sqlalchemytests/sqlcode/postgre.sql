-- sudo -u postgres psql evalance
-- CREATE DATABASE evalance;
-- sudo -u postgres python learning.py

-- --------------------------------------------------------
-- Name: clean_tables
-- --------------------------------------------------------
DROP VIEW IF EXISTS merged_tables; -- must be dropped before the others
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
-- Name: user_insertion_template
-- --------------------------------------------------------
INSERT INTO users (password_hash, first_name, mid_name, last_name, age)
VALUES ('{password_hash}', '{first_name}', '{mid_name}', '{last_name}', {age});

-- --------------------------------------------------------
-- Name: team_insertion_template
-- --------------------------------------------------------
INSERT INTO teams (team_name)
VALUES ('{team_name}');

-- --------------------------------------------------------
-- Name: membership_insertion_template
-- --------------------------------------------------------
INSERT INTO memberships (team_id, user_id, role, cost)
VALUES ({team_id}, {user_id}, '{role}', {cost});

-- --------------------------------------------------------
-- Name: users_not_in_team
-- Gets all users not in a team (user id)
-- --------------------------------------------------------
SELECT users.user_id -- , memberships.team_id -> check that they are really nulls :D
FROM users
    LEFT JOIN  memberships
    ON memberships.user_id = users.user_id
WHERE memberships.team_id IS NULL;

-- --------------------------------------------------------
-- Name: team_cost
-- Calculates the avg cost of each team (team name, cost)
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
-- Name: merge_tables_view
-- Creates a table that joins the users, memberships and
-- teams tables.
-- --------------------------------------------------------
CREATE VIEW merged_tables AS
    SELECT *
    FROM users
        JOIN memberships
        USING (user_id)
        JOIN teams
        USING (team_id);

SELECT * from merged_tables;

-- --------------------------------------------------------
-- Name: two_column_group_by
-- Uses a two columns "group by" to get the maximum cost of
-- the each role in a team. Then it uses a join to recover
-- the names of each team and orders for presentation.
-- --------------------------------------------------------
SELECT teams.team_name, teams.team_id, role, MAX(cost) AS max_cost
FROM merged_tables
    JOIN teams
    ON merged_tables.team_id = teams.team_id
GROUP BY teams.team_id, role
ORDER BY teams.team_id DESC;

-- --------------------------------------------------------
-- Name: one_user_n_teams
-- Retrieves all users that are part of more than one team.
-- As we are using a window function, we need to sub select
-- in order to filter with where.
-- --------------------------------------------------------
SELECT user_id, number_of_teams
FROM ( SELECT DISTINCT user_id, COUNT(user_id) OVER(PARTITION BY user_id) AS number_of_teams
       FROM merged_tables
     ) AS temp_alias
WHERE number_of_teams >= 2;

-- --------------------------------------------------------
-- Name: teams_with_shared_member
-- Retrieves the names of the teams with members that form
-- part of another team. Uses a similar strategy than the
-- last query.
-- --------------------------------------------------------
SELECT DISTINCT team_name
FROM ( SELECT team_id, team_name, COUNT(user_id) OVER(PARTITION BY user_id) AS number_of_teams
       FROM merged_tables
     ) AS temp_alias
WHERE number_of_teams >= 2;

-- --------------------------------------------------------
-- Name: window_avg_team_cost
-- Calculates the average team cost using a window function.
-- --------------------------------------------------------
SELECT DISTINCT team_id, AVG(cost) OVER w as team_cost
FROM teams
    JOIN memberships
    USING (team_id)
WINDOW w AS (PARTITION BY team_id)
ORDER BY team_id ASC;
-- it is more succinct than its group by alternative
-- SELECT teams.team_id, AVG(memberships.cost) as team_cost
-- FROM users
--    JOIN memberships
--    ON memberships.user_id = users.user_id
--    JOIN teams
--    ON memberships.team_id = teams.team_id
-- GROUP BY teams.team_id
-- ORDER BY team_id ASC;

-- --------------------------------------------------------
-- Name: more_than_one_role
-- Gets the users and roles of people with more than one role.
-- --------------------------------------------------------
SELECT user_id, role
FROM (SELECT user_id, role, COUNT(*) OVER (PARTITION BY user_id) as num_roles
        FROM memberships) AS non_used_alias
WHERE num_roles > 1;


-- --------------------------------------------------------
-- Name: temp_table_creation_1
-- Creates a temporary table inserting a select statement.
-- --------------------------------------------------------
-- CREATE OR REPLACE does work in PostgreSQL?
-- When no select is used () is needed (with or without columns)
DROP TABLE IF EXISTS temp_table_1;
CREATE TEMPORARY TABLE temp_table_1 (full_name VARCHAR(50))
ON COMMIT PRESERVE ROWS;
INSERT INTO temp_table_1
SELECT (SELECT CONCAT(first_name, ' ',
                  COALESCE(CONCAT(mid_name, ' ')),
                  last_name)

       FROM users);

-- --------------------------------------------------------
-- Name: temp_table_creation_2
-- Creates a temporary table using a select statement as part
-- of the creation.
-- --------------------------------------------------------
DROP TABLE IF EXISTS temp_table_2;
-- Here () is not needed
CREATE TEMPORARY TABLE  temp_table_2
AS (SELECT CONCAT(first_name, ' ',
                  COALESCE(CONCAT(mid_name, ' ')),
                  last_name)
    FROM users)
ON COMMIT PRESERVE ROWS;

-- --------------------------------------------------------
-- Name: temp_table_creation_3
-- Creates a temporary table using the VALUES statement.
-- --------------------------------------------------------
DROP TABLE IF EXISTS temp_table_3;
CREATE TEMPORARY TABLE  temp_table_3 (  first_name  VARCHAR(20),
                                        mid_name    VARCHAR(20),
                                        last_name   VARCHAR(20),
                                        role        VARCHAR(20))
ON COMMIT PRESERVE ROWS;

INSERT INTO temp_table_3
    VALUES  ('Victor', 'Alejandro', 'Gil', 'Software Developer'),
            ('Conan', 'the Cimmerian', '', 'Barbarian / King'),
            ('Peter', '', 'Parker', 'Vigilante'),
            ('James', 'Tiberius', 'Kirk', 'Starship Captain');

-- --------------------------------------------------------
-- Name:
-- Work in progress (in Join and ...)
-- --------------------------------------------------------
#---------------------------------------------------
# Get the memberships with costs with at least 3 floating
# point positions
#---------------------------------------------------

CREATE OR REPLACE FUNCTION GET_NTH_DEC_RESIDUE(NUMERIC, INTEGER) RETURNS NUMERIC AS
$function$
    SELECT CAST(CAST($1 AS NUMERIC) * POW(10,$2) - FLOOR(CAST($1 AS NUMERIC)*POW(10,$2)) AS NUMERIC);
$function$
LANGUAGE SQL;

SELECT user_id, cost, nth_pos_dec
FROM (SELECT user_id, GET_NTH_DEC_RESIDUE(CAST(memberships.cost AS NUMERIC), 2) AS nth_pos_dec
      FROM users
        JOIN memberships
        USING (user_id)) AS T
WHERE NOT (nth_pos < 1.0 AND  nth_pos >= 0.0);

#---------------------------------------------------
# Get the memberships with costs with exactly 2
# floating point positions
#---------------------------------------------------

-- triggers