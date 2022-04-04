import sqlite3
import contextlib
import logging.config

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    database: str
    logging_config: str

    class Config:
        env_file = "word-validation.env"


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db

def get_logger():
    return logging.getLogger(__name__)

settings = Settings()
app = FastAPI()

logging.config.fileConfig(settings.logging_config)

# list all valid 5 letter guesses from database
@app.get("/words/")
def list_books(db: sqlite3.Connection = Depends(get_db)):
    words = db.execute("SELECT * FROM words")
    return {"words": words.fetchall()}


# check if the guess is valid. returns word if valid, otherwise returns error 404
@app.get("/words/{word}")
def valid_word(
    word: str, reponse: Response, db: sqlite3.Connection = Depends(get_db)
):
    cur = db.execute("select * from words where word = ?", [word])
    words = cur.fetchall()
    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not a valid guess"
        )
    return {"words": word}
