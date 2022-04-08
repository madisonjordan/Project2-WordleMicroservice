import sqlite3
import contextlib
import logging.config
import typing

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseSettings


class Settings(BaseSettings):
    database: str
    logging_config: str

    class Config:
        env_file = "answer.env"


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db

def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()

logging.config.fileConfig(settings.logging_config)

guess = "zones"
answer = "zebra"

for x in range(len(answer)):
    if f"{answer}"[x] == f"{guess}"[x]:
        print(f"{guess}"[x], " - correct position")
    elif f"{guess}"[x] in f"{answer}":
        print(f"{guess}"[x], " - exists")
    else:
        print(f"{guess}"[x], " - not found")

@app.get("/answers/")
def list_answers(db: sqlite3.Connection = Depends(get_db)):
    answers = db.execute("SELECT * FROM answers")
    return {"answer": answers.fetchall()}
