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
    streaks = db.execute("SELECT * FROM streaks WHERE user_id = ? ORDER BY streak DESC", [user_id])
    user_streaks = streaks.fetchall()
    max_streak = user_streaks[0]
    if not user_streaks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    return {"max streak": max_streak}
