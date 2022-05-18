import contextlib
import logging.config
import sqlite3
from typing import Optional
import json
import datetime
from datetime import date
from sqlite_utils import Database

from fastapi import FastAPI, Depends, Response, HTTPException, Body
from pydantic import BaseModel, BaseSettings
from typing import Optional, List, Literal


class Settings(BaseSettings):
    database: str = "./var/answers.db"
    logging_config: str = "./etc/logging.ini"
    openapi_url: str = "/openapi.json"

    class Config:
        env_file = "answers.env"


class Answer(BaseModel):
    day: int = int(datetime.date.today().strftime("%Y%m%d"))
    word: str


class Letters(BaseModel):
    correct: list
    present: list


class Check(BaseModel):
    isCorrect: Literal["incorrect", "correct"]
    letters: Letters


settings = Settings()
app = FastAPI(root_path="/api/answer", openapi_url=settings.openapi_url)


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


# get WOTD based on the date parameter entered
@app.get("/answers/{day}")
def get_answer(
    day: int = int(datetime.date.today().strftime("%Y%m%d")),
    db: sqlite3.Connection = Depends(get_db),
):
    cur = db.execute("SELECT word FROM answers WHERE day = ?", [day])
    wotd = cur.fetchall()
    if not wotd:
        raise HTTPException(status_code=404, detail="No Answer for this Day")
    return wotd


@app.get("/answers")
def get_all_answers(response: Response, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("SELECT * FROM answers")
    wotd = cur.fetchall()
    return wotd


@app.put("/answers")
def change_answer(
    answer: Answer,
    db: sqlite3.Connection = Depends(get_db),
):
    word = dict(answer)
    sql = "update answers set word=:word where day=:day"
    cur = db.execute(sql, word)
    cur = db.execute("SELECT * FROM answers WHERE day=:day LIMIT 1", word)
    db.commit()
    wotd = cur.fetchall()
    if not wotd:
        raise HTTPException(
            status_code=404,
            detail="No Answer for this Day",
        )
    return wotd


# check guess against today's answer in answers.db
@app.get("/check/{guess}", response_model=Check)
def find_answer(
    guess: str,
    day: Optional[int] = int(datetime.date.today().strftime("%Y%m%d")),
    db: sqlite3.Connection = Depends(get_db),
    logger: logging.Logger = Depends(get_logger),
):
    guess = guess
    cur = db.execute("SELECT word FROM answers WHERE day = ? LIMIT 1", [day])
    answer = cur.fetchone()
    if not answer:
        raise HTTPException(
            status_code=404,
            detail="No Answer for this Day",
        )
    answer = answer[0]
    correct = []
    present = []
    for x in range(len(guess)):
        curr_letter = f"{guess}"[x]
        if guess[x] == f"{answer}"[x]:
            correct.append(curr_letter)
        elif f"{guess}"[x] in f"{answer}":
            present.append(curr_letter)
        else:
            pass

    if len(correct) == len(guess):
        status = "correct"
    else:
        status = "incorrect"

    return {"status": status, "letters": {"correct": correct, "present": present}}
