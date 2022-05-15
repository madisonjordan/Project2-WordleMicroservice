import asyncio
import httpx
import json
from pydantic import BaseModel
import pydantic.json as pydanticjson
from typing import Optional
import datetime


from answers import app as answer_service
from words import app as word_service
from stats import app as stats_service
from game_state import app as game_state_service


class User(BaseModel):
    username: str
    user_id: Optional[str]


class Game(BaseModel):
    user_id: str
    game_id: Optional[int] = int(datetime.date.today().strftime("%Y%m%d"))


class Guess(BaseModel):
    user_id: str
    guess: str
    game_id: Optional[int] = int(datetime.date.today().strftime("%Y%m%d"))


# get user_id from stats service
def getUser(username: str):
    # with httpx.Client(app=stats_service, base_url="http://127.0.0.1:9999") as client:
    response = httpx.get(f"http://127.0.0.1:9999/users/{username}")
    # user_data = json.loads(r.text)
    print(response.url)
    # print(r.status_code)
    # print(json.dumps(user_data, indent=4))
    # get user_id
    return response.json()


# TODO: create new game
def create_game(game: Game):
    headers = {"content-type": "application/json"}
    # with httpx.Client(app=game_state_service, headers=headers) as client:
    # print(headers["content-type"])
    response = httpx.post("http://127.0.0.1:9999/game/new", data=game, headers=headers)
    # print(game.get("user_id"))
    # print(game.get("game_id"))
    # print(response.request.url)
    print(response.url)
    print(response.text)


# TODO: check if user has guesses remaining in this game
async def isValidGame():
    async with httpx.AsyncClient(
        app=game_state_service, base_url="http://127.0.0.1:9999"
    ) as client:
        r = await client.get("/game/")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: check if word is valid guess
async def isValidWord(guess: str):
    async with httpx.AsyncClient(
        app=word_service, base_url="http://127.0.0.1:9999"
    ) as client:
        r = await client.get("/word/", guess)
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: check if valid guess is correct answer
async def check_guess():
    async with httpx.AsyncClient(
        app=answer_service, base_url="http://127.0.0.1:9999"
    ) as client:
        r = await client.get("/check/soaps")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: post user's guess to game
async def update_game():
    async with httpx.AsyncClient(
        app=game_state_service, base_url="http://127.0.0.1:9999"
    ) as client:
        r = await client.post("/game/")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: update user stats if this game is finished
async def updateStats():
    async with httpx.AsyncClient(
        app=stats_service, base_url="http://127.0.0.1:9999"
    ) as client:
        r = await client.post("/users/b07ecefc-a928-4b3a-a418-cb8930dd93b4")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: return user stats
async def getStats():
    async with httpx.AsyncClient(
        app=stats_service, base_url="http://127.0.0.1:9999"
    ) as client:
        r = await client.get("/users/b07ecefc-a928-4b3a-a418-cb8930dd93b4/stats")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: workflow for adding a new guess
# input: username or user_id (pick one)
# output:
# error conditions:
#   - game doesn't exist
#   - game has ended
#   - word isn't valid
def new_guess(guess=Guess):
    user_id = guess.get("user_id")
    game_id = guess.get("game_id")
    word = guess.get("guess")

    # check if game is valid
    isValidGame(user_id, game_id)

    # check if word is valid
    isValidWord()


# TODO: workflow for adding a new game
# input: username
# output: game state of this game
# error conditions:
#   - game id already exists (conflict)


def new_game(username: User):
    user = getUser(username)
    # print for debugging
    print("getUser():\n\t", user, "\n")
    user = user.get("user_id")
    # print(user)
    game = Game(user_id=user).json()
    # print for debugging
    print("Game model object:\n\t", game, "\n")
    # TODO: create_game passing game object
    create_game(json.dumps(game))
    create_game(game)
    game = Game(user_id=user).__dict__
    create_game(game)
    create_game(json.dumps(game))


# test new game() for endpoint
user1 = "christina22"
new_game(user1)

# TEST async
# asyncio.run(getUser(user1))
# asyncio.run(getStats())
# asyncio.run(check_guess())


# run concurrently


###########
# Example #
###########
# define tasks to run concurrently
# async def main():

# run concurrently
# asyncio.run(main())
