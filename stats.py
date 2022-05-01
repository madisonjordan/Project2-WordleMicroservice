from os import stat
import sqlite3
import uuid
import sqlite_utils
import datetime
import contextlib
import logging.config
import collections
import itertools

from fastapi import FastAPI, Depends, Response, HTTPException, status, Request
from pydantic import BaseModel, BaseSettings

# use UUID in table
sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)


class Settings(BaseSettings):
    database_dir: str
    logging_config: str
    shards: int

    class Config:
        env_file = "stats.env"


class Game(BaseModel):
    user_id: str
    finished: datetime.date
    guesses: int
    won: bool


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


@app.get("/users/{user_id}/stats")
def get_stats(user_id: str, response: Response):
    shard = getShardId(user_id)
    db = sqlite3.connect(f"{settings.database_dir}stats{shard}.db")
    max_streak = db.execute(
        "SELECT streak FROM streaks WHERE user_id = ? ORDER BY streak DESC LIMIT 1",
        [user_id],
    )
    # streaks for this user
    max_streak = max_streak.fetchone()
    if not max_streak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    curr_streak = db.execute(
        "SELECT streak FROM streaks WHERE user_id = ? ORDER BY ending DESC LIMIT 1",
        [user_id],
    )
    curr_streak = curr_streak.fetchone()
    # num games
    games_played = db.execute(
        "SELECT COUNT(*) FROM games WHERE user_id = ? LIMIT 1", [user_id]
    )
    games_played = games_played.fetchone()
    # num wins and losses
    wins = db.execute("SELECT wins FROM wins WHERE user_id = ? LIMIT 1", [user_id])
    wins = wins.fetchone()
    losses = games_played[0] - wins[0]
    # count of guesses in each win, or count of fails
    guesses = db.execute(
        "SELECT COUNT(guesses) FROM games WHERE user_id = ? AND won = TRUE GROUP BY guesses",
        [user_id],
    )
    guesses_query = guesses.fetchall()
    guesses = {
        "1": guesses_query[0][0],
        "2": guesses_query[1][0],
        "3": guesses_query[2][0],
        "4": guesses_query[3][0],
        "5": guesses_query[4][0],
        "6": guesses_query[5][0],
        "failed": losses,
    }
    # average guesses for wins
    sum = 0
    for i in range(6):
        key = i + 1
        sum += key * guesses[f"{key}"]
    avg_guesses = sum / wins[0]

    avg_wins = wins[0] / games_played[0]

    return {
        "currentStreak": curr_streak[0],
        "maxStreak": max_streak[0],
        "guesses": guesses,
        "winPercentage": avg_wins,
        "gamesPlayed": games_played[0],
        "gamesWon": wins[0],
        "averageGuesses": avg_guesses,
    }


@app.post("/users/", status_code=status.HTTP_201_CREATED)
def create_game_stats(game: Game, response: Response):
    g = dict(game)
    user = g.get("user_id")
    shard = getShardId(user)
    db = sqlite3.connect(f"{settings.database_dir}stats{shard}.db")
    db = sqlite3.connect(f"./var/stats{shard}.db")

    try:
        games_played = db.execute(
            "SELECT COUNT(*) FROM games WHERE user_id=:user_id LIMIT 1", g
        )
        games_played = games_played.fetchone()[0]
        g["game_id"] = games_played + 1
        cur = db.execute(
            """
            INSERT INTO games(user_id, game_id, finished, guesses, won)
            VALUES(:user_id, :game_id, :finished, :guesses, :won)
            """,
            g,
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    return g


@app.get("/top10/streaks/all")
def top10_streaks_all_time():
    shard_top10 = collections.defaultdict(list)
    temp = []
    all_list = []
    top10 = []
    for shard in range(settings.shards):
        db = sqlite3.connect(f"{settings.database_dir}stats{shard}.db")
        shard_top10[shard] = db.execute(
            "SELECT streaks.user_id, users.username, streaks.streak FROM streaks INNER JOIN users ON streaks.user_id=users.user_id ORDER BY streak DESC LIMIT 10"
        ).fetchall()
        temp.append(shard_top10[shard])
    all_list = list(itertools.chain(*temp))
    # sort by streaks (index 2)
    all_list.sort(reverse=True, key=lambda x: x[2])
    for user in range(10):
        user_streak = {
            "user_id": all_list[user][0],
            "username": all_list[user][1],
            "streak": all_list[user][2],
        }
        top10.append(user_streak)
    return top10


@app.get("/top10/wins")
def top10_wins():
    shard_top10 = collections.defaultdict(list)
    temp = []
    all_list = []
    top10 = []
    for shard in range(settings.shards):
        db = sqlite3.connect(f"{settings.database_dir}stats{shard}.db")
        shard_top10[shard] = db.execute(
            "SELECT wins.user_id, users.username, wins.wins FROM wins INNER JOIN users ON wins.user_id=users.user_id ORDER BY wins DESC LIMIT 10"
        ).fetchall()
        temp.append(shard_top10[shard])
    all_list = list(itertools.chain(*temp))
    # sort by wins (index 2)
    all_list.sort(reverse=True, key=lambda x: x[2])
    for user in range(10):
        user_wins = {
            "user_id": all_list[user][0],
            "username": all_list[user][1],
            "wins": all_list[user][2],
        }
        top10.append(user_wins)
    return top10
