from fastapi import (
    FastAPI,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, BaseSettings
import redis
import json
from typing import Optional, Literal
import datetime


class Settings(BaseSettings):
    logging_config: str = "./etc/logging.ini"
    openapi_url: str = "/openapi.json"

    class Config:
        env_file = "game_state.env"


settings = Settings()
app = FastAPI(root_path="/api/state", openapi_url=settings.openapi_url)
# start connection to redis server
r = redis.Redis(host="localhost", port=6379, db=0)

# defines a new game in request body
class Guess(BaseModel):
    user_id: str
    guess: str


class GameState(BaseModel):
    status: Optional[str]
    user_id: str
    game_id: int = int(datetime.date.today().strftime("%Y%m%d"))
    remaining: Optional[int] = 6
    guesses: Optional[list] = []


class Message(BaseModel):
    message: str


# get game status
@app.get(
    "/users/{user_id}/game/{game_id}",
    response_model=GameState,
    response_model_exclude_unset=True,
    responses={
        404: {"model": Message, "description": "The game was not found"},
        200: {
            "description": "Created New Game",
            "content": {
                "application/json": {
                    "example": {
                        "status": "in-progress",
                        "user_id": "6b6c3a30-c0dd-4df5-acfc-a00fc51fb5f3",
                        "game_id": "48",
                        "remaining": 5,
                        "guesses": [],
                    }
                }
            },
        },
    },
)
def get_game(user_id: str, game_id: int):
    res = r.hmget(user_id, game_id)
    # if game is already played return error
    if res[0] == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has not started this game.",
        )
    # gets game object from redis
    game_state = json.loads(res[0])
    return game_state


# start a new game
@app.post(
    "/game/new",
    response_model=GameState,
    response_model_exclude_defaults=True,
    responses={
        403: {
            "model": Message,
            "description": "A game with this game id already exists for this user",
        },
        201: {
            "description": "Created New Game",
            "content": {
                "application/json": {
                    "example": {
                        "status": "new",
                        "user_id": "6b6c3a30-c0dd-4df5-acfc-a00fc51fb5f3",
                        "game_id": 48,
                    }
                }
            },
        },
    },
)
def new_game(game: GameState):
    res = r.hmget(game.user_id, game.game_id)
    if res[0] != None:
        return JSONResponse(
            status_code=403, content={"message": "Game ID already exists for this user"}
        )
    # create new game in json format so it can be set in redis
    new_game = GameState(
        status="new", user_id=game.user_id, game_id=game.game_id
    ).json()
    new_game = json.loads(new_game)
    # set the new game object with user_id as the key
    r.hmset(
        game.user_id,
        {game.game_id: json.dumps(new_game)},
    )
    return new_game


# update game with new guess
@app.post(
    "/game/{game_id}/new",
    response_model=GameState,
    responses={
        404: {"model": Message, "description": "The game was not found"},
        200: {
            "description": "Added new guess",
            "content": {
                "application/json": {
                    "example": {
                        "status": "in-progress",
                        "user_id": "6b6c3a30-c0dd-4df5-acfc-a00fc51fb5f3",
                        "game_id": 48,
                        "remaining": 5,
                        "guesses": ["forge"],
                    }
                }
            },
        },
    },
)
def add_guess(game_id: int, guess: Guess):
    data = json.loads(guess.json())
    user_id = data.get("user_id")
    guess = data.get("guess")
    res = r.hmget(user_id, game_id)
    # if game is already played return error
    if res[0] == None:
        raise HTTPException(status_code=400, detail="Failed to add guess")
    # gets game object from redis
    game_state = json.loads(res[0])
    # check if game is already complete
    if game_state["status"] == "new":
        game_state["status"] = "in-progress"
    elif game_state["status"] == "finished":
        raise HTTPException(status_code=403, detail="This game has ended")
    # add new guess and update remaining attempts
    game_state["remaining"] -= 1
    game_state["guesses"].append(guess)
    # update status if finished
    if game_state["remaining"] == 0:
        game_state["status"] = "finished"
    # save changes
    mapping = json.dumps(game_state)
    r.hmset(
        user_id,
        {game_id: mapping},
    )
    return game_state


# mark game as complete if guess is correct
@app.put(
    "/users/{user_id}/game/{game_id}",
    response_model=GameState,
    responses={
        404: {"model": Message, "description": "The game was not found"},
        200: {
            "description": "Game finished successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "finished",
                        "user_id": "6b6c3a30-c0dd-4df5-acfc-a00fc51fb5f3",
                        "game_id": 48,
                        "remaining": 5,
                        "guesses": ["forge"],
                    }
                }
            },
        },
    },
)
def mark_complete(game_id: int, user_id: str):
    res = r.hmget(user_id, game_id)
    if res[0] == None:
        raise HTTPException(status_code=400, detail="Game ID Not Found")
    # gets game object from redis
    game_state = json.loads(res[0])
    game_state["status"] = "finished"
    mapping = json.dumps(game_state)
    r.hmset(
        user_id,
        {game_id: mapping},
    )
    return game_state
