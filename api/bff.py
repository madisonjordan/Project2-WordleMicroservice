import asyncio
from urllib import response
import httpx
import json
from pydantic import BaseModel
from typing import Optional, Literal
import datetime
from fastapi.encoders import jsonable_encoder


from answers import app as answer_service
from words import app as word_service
from stats import app as stats_service
from game_state import app as game_state_service

# input/output models for bff service endpoints
class User(BaseModel):
    username: str
    user_id: Optional[str]


class Game(BaseModel):
    user_id: str
    game_id: Optional[int] = int(datetime.date.today().strftime("%Y%m%d"))


class Guess(BaseModel):
    user_id: str
    guess: str


# get user_id from stats service
def getUser(username: str):
    with httpx.Client(base_url="http://localhost:9999/api/statistics") as client:
        response = client.get(f"/users/{username}")
        # user_data = json.loads(r.text)
        print(response.url)
        # print(r.status_code)
        # print(json.dumps(user_data, indent=4))
        # get user_id
        return response.json()


# create new game
def create_game(game: Game):
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/state") as client:
        response = client.post("/game/new", data=game, headers=headers)
        # print(game.get("user_id"))
        # print(game.get("game_id"))
        # print("===================\n")
        # print("request:\n", response.request.url)
        # print(headers)
        # print(game)
        # print("\nresponse:\n", response.url)
        print(response.text)


# get current game state
def getGame(game: Game):
    game_id = game.get("game_id")
    user_id = game.get("user_id")
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/state") as client:
        response = client.get(f"users/{user_id}/game/{game_id}", headers=headers)
        print(response.status_code)
        text = json.loads(response.text)
        print(json.dumps(text, indent=4))


# check if user has guesses remaining in this game
def isValidGame(game: Game):
    game_id = game.get("game_id")
    user_id = game.get("user_id")
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/state") as client:
        response = client.get(f"users/{user_id}/game/{game_id}", headers=headers)
        text = json.loads(response.text)
        status = text.get("status")
        if status == "finished":
            return False
        else:
            return True


# check if word is valid guess
def isValidWord(guess: str):
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/word") as client:
        response = client.get(f"/words/{guess}", headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False


# check if guess is correct
def check_guess(guess: str, day: int):
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/answer") as client:
        response = client.get(f"/check/{guess}", params={"day": day}, headers=headers)
        print(response.status_code)
        print(json.dumps(json.loads(response.text), indent=4))
        # check if the guess is correct from the response
        text = json.loads(response.text)
        status = text.get("status")
        if status == "correct":
            return True
        else:
            return False


# post user's guess to game
def add_guess(game: Game, guess: str):
    # load game data
    game_id = game.get("game_id")
    user = game.get("user_id")
    # build Guess model to pass to game_state service
    current_guess = Guess(user_id=user, guess=guess).json()
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/state") as client:
        response = client.post(f"/game/{game_id}", data=current_guess, headers=headers)
        print(response.status_code)
        print(json.dumps(json.loads(response.text), indent=4))


# TODO: update user stats if this game is finished
async def updateStats():
    async with httpx.AsyncClient(
        app=stats_service, base_url="http://localhost:9999/api/statistics"
    ) as client:
        r = await client.post("/users/b07ecefc-a928-4b3a-a418-cb8930dd93b4")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: return user stats
async def getStats():
    async with httpx.AsyncClient(
        app=stats_service, base_url="http://localhost:9999/api/statistics"
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
def new_guess(game_id: int, guess: Guess):
    # get user from guess request body
    user = guess.get("user_id")
    # create game object
    game = Game(user_id=user, game_id=game_id).json()
    # get guess string from guess request body
    current_guess = guess.get("guess")

    # check if game is valid
    print("\nisValidGame():")
    if isValidGame(json.loads(game)):
        print("True")
    else:
        # raise 400 error - bad request and get remaining guesses from game state
        print("False")

    # check if word is valid
    print("\nisValidWord():")
    if isValidWord(current_guess):
        print("True")
    else:
        print("False")

    # add new guess to game
    print("\nadd_guess():")
    add_guess(json.loads(game), current_guess)

    # check if guess is correct
    print("\ncheck_guess():")
    if check_guess(current_guess, game_id):
        print("True")
    else:
        print("False")


# TODO: workflow for adding a new game
# input: username
# output: game state of this game
# error conditions:
#   - game id already exists (conflict)
def new_game(username: User):
    # game_id test value - when not using default (today)
    test_gameid = 20220501
    # get user_id
    user = getUser(username)
    # print values for getUser response
    print("getUser():\n\t", user, "\n")
    user = user.get("user_id")
    # create new game object using user and default game_id
    game = Game(user_id=user).json()
    game = Game(user_id=user, game_id=test_gameid).json()
    # print for debugging
    print("Game model object:\n\t", game, "\n")
    print("\ncreate_game():")
    # pass new game object and create new game
    create_game(game)
    print("\ngetGame():")
    getGame(json.loads(game))
    guess = Guess(user_id=user, guess="pilot").json()
    new_guess(test_gameid, json.loads(guess))


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
