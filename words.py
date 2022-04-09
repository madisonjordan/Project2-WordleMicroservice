import sqlite3
import contextlib
import logging.config

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseSettings


class Settings(BaseSettings):
    database: str
    logging_config: str

    class Config:
        env_file = "words.env"


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()

logging.config.fileConfig(settings.logging_config)

# list all valid guesses from word database
@app.get("/words/")
def list_books(db: sqlite3.Connection = Depends(get_db)):
    words = db.execute("SELECT * FROM words")
    return {"word": words.fetchall()}


# check if the guess is valid. returns word if valid, otherwise returns error 404
@app.get("/words/{word}")
def valid_word(word: str, reponse: Response, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("select * from words where word = ?", [word])
    words = cur.fetchall()
    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not a valid guess"
        )
    return {"word": word}


# add new word to database
@app.post("/words/", status_code=status.HTTP_201_CREATED)
def create_word(
    word: str, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    w = [word]
    try:
        cur = db.execute(
            """
            INSERT INTO words(word)
            VALUES(:word)
            """,
            w,
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    return w


@app.delete("/words/{word}")
def delete_word(word: str, reponse: Response, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("DELETE FROM words WHERE word = ?", [word])
    db.commit()
    return {"ok": True}
