DROP VIEW IF EXISTS wins;
DROP VIEW IF EXISTS streaks;
DROP INDEX IF EXISTS games_won_idx;

CREATE TABLE users_new(
    user_id GUID PRIMARY KEY, 
    id INT NOT NULL,
    username VARCHAR UNIQUE
);

INSERT INTO users_new (user_id, id, username)
SELECT user_id, user_id, username
FROM users;

DROP TABLE users;

ALTER TABLE users_new
RENAME TO users;