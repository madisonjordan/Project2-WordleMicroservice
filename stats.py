import sqlite3
import uuid
import sqlite_utils
import datetime
import contextlib
import logging.config
import collections

from fastapi import FastAPI, Depends, Response, HTTPException, status, Request
from pydantic import BaseSettings

# use UUID in table
sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)


class Settings(BaseSettings):
    database_dir: str
    logging_config: str
    shards: int

    class Config:
        env_file = "stats.env"


settings = Settings()
app = FastAPI(openapi_url="/api/v1/openapi.json")


def getShardId(string_uuid):
    curr_uuid = uuid.UUID(string_uuid)
    return curr_uuid.int % settings.shards


@app.get("/users/")
def list_users():
    for shard in range(settings.shards):
        db = sqlite3.connect(f"{settings.database_dir}stats{shard}.db")
        users = db.execute("SELECT * FROM users")
        yield {"stats_db": shard, "users": users.fetchall()}


@app.get("/users/{user_id}")
def get_user(user_id: str, response: Response):
    shard = getShardId(user_id)
    db = sqlite3.connect(f"{settings.database_dir}stats{shard}.db")
    cur = db.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
    user = cur.fetchall()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    return {"user": user}


@app.get("/stats/{user_id}")
def get_stats(user_id: str, response: Response):
    shard = getShardId(user_id)
    db = sqlite3.connect(f"{settings.database_dir}stats{shard}.db")
    max_streak = db.execute(
        "SELECT streak FROM streaks WHERE user_id = ? ORDER BY streak DESC LIMIT 1",
        [user_id],
    )
    max_streak = max_streak.fetchone()
    if not max_streak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    curr_streak = db.execute(
        "SELECT streak FROM streaks WHERE user_id = ? LIMIT 1", [user_id]
    )
    curr_streak = curr_streak.fetchone()
    guesses = db.execute(
        "SELECT COUNT(guesses) FROM games WHERE user_id = ? GROUP BY guesses", [user_id]
    )
    guesses_query = guesses.fetchall()
    guesses = {
        "1": guesses_query[0][0],
        "2": guesses_query[1][0],
        "3": guesses_query[2][0],
        "4": guesses_query[3][0],
        "5": guesses_query[4][0],
        "6": guesses_query[5][0]
    }
    avg_guesses = db.execute(
        "SELECT AVG(guesses) FROM games WHERE user_id = ? LIMIT 1", [user_id]
    )
    avg_guesses = avg_guesses.fetchone()
    games_played = db.execute(
        "SELECT COUNT(*) FROM games WHERE user_id = ? LIMIT 1", [user_id]
    )
    games_played = games_played.fetchone()
    wins = db.execute("SELECT wins FROM wins WHERE user_id = ? LIMIT 1", [user_id])
    wins = wins.fetchone()
    avg_wins = wins[0] / games_played[0]

    return {
        "currentStreak": curr_streak[0],
        "maxStreak": max_streak[0],
        "guesses": guesses,
        "winPercentage": avg_wins,
        "gamesPlayed": games_played[0],
        "gamesWon": wins[0],
        "averageGuesses": avg_guesses[0],
    }
