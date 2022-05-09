PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS games_new;

CREATE TABLE games_new(
    user_id GUID, 
    game_id INTEGER NOT NULL,
    finished DATE DEFAULT CURRENT_TIMESTAMP,
    guesses INTEGER,
    won BOOLEAN,
    PRIMARY KEY(user_id, game_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

INSERT INTO games_new (user_id, game_id, finished, guesses, won)  
SELECT users.user_id, games.game_id, games.finished, games.guesses, games.won FROM games, users
WHERE users.id=games.user_id;

DROP TABLE games;

ALTER TABLE games_new RENAME TO games;

CREATE INDEX games_won_idx ON games(won);

CREATE VIEW wins
AS
    SELECT
        user_id,
        COUNT(won) AS wins
    FROM
        games
    WHERE
        won = TRUE
    GROUP BY
        user_id
    ORDER BY
        COUNT(won) DESC;

CREATE VIEW streaks
AS
    WITH ranks AS (
        SELECT DISTINCT
            user_id,
            finished,
            RANK() OVER(PARTITION BY user_id ORDER BY finished) AS rank
        FROM
            games
        WHERE
            won = TRUE
        ORDER BY
            user_id,
            finished
    ),
    groups AS (
        SELECT
            user_id,
            finished,
            rank,
            DATE(finished, '-' || rank || ' DAYS') AS base_date
        FROM
            ranks
    )
    SELECT
        user_id,
        COUNT(*) AS streak,
        MIN(finished) AS beginning,
        MAX(finished) AS ending
    FROM
        groups
    GROUP BY
        user_id, base_date
    HAVING
        streak > 1
    ORDER BY
        user_id,
        finished;

PRAGMA analysis_limit=1000;
PRAGMA optimize;