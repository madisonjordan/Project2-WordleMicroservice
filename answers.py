import collections
import contextlib
import logging.config
import sqlite3
import typing
import json
import datetime
from datetime import date


from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    database: str
    logging_config: str

    class Config:
        env_file = "answers.env"


settings = Settings()
app = FastAPI()


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


# get WOTD based on the date parameter entered
@app.get("/answers/{date}")
def get_answer(date: str, response: Response, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("SELECT word FROM answers WHERE day = ?", [date])
    wotd = cur.fetchall()
    if not wotd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Answer for this Day",
        )
    return {"word": wotd}


# check guess against today's answer in answers.db
@app.get("/check/{guess}")
def find_answer(
    guess: str,
    db: sqlite3.Connection = Depends(get_db),
    logger: logging.Logger = Depends(get_logger),
):
    guess = guess
    day = datetime.date.today()
    logger.debug(f"{day}")
    cur = db.execute(
        "SELECT word FROM answers WHERE day = ? LIMIT 1", [day.strftime("%Y-%m-%d")]
    )
    answer = cur.fetchone()
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Answer for this Day"
        )
    answer = answer[0]
    check = [len(guess)]
    for x in range(len(guess)):
        curr_letter = f"{guess}"[x]
        if guess[x] == f"{answer}"[x]:
            check_pos = "correct"
        elif f"{guess}"[x] in f"{answer}":
            check_pos = "exists"
        else:
            check_pos = "not in answer"

        check.append(
            {"position": f"{x}", "letter": f"{curr_letter}", "check": f"{check_pos}"}
        )

    return check
