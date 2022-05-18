import asyncio
from urllib import response
import httpx
import json
from pydantic import BaseModel, BaseSettings
from typing import Optional, Literal
import datetime
from fastapi import FastAPI, Depends, Response, HTTPException, Body


from answers import app as answer_service
from words import app as word_service
from stats import app as stats_service
from game_state import app as game_state_service


class Settings(BaseSettings):
    logging_config: str = "./etc/logging.ini"
    openapi_url: str = "/api/bff/openapi.json"


# input/output models for bff service endpoints
class User(BaseModel):
    username: str


class Guess(BaseModel):
    user_id: str
    guess: str


class Game(BaseModel):
    user_id: str
    game_id: int = int(datetime.date.today().strftime("%Y%m%d"))
    finished: Optional[datetime.date] = datetime.date.today()
    guesses: Optional[int]
    won: Optional[bool] = False


# get user_id from stats service
def getUser(username: str):
    with httpx.Client(base_url="http://localhost:9999/api/statistics") as client:
        response = client.get(f"/users/{username}")
        return response


# create new game
def create_game(game: Game):
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/state") as client:
        response = client.post("/game/new", data=game, headers=headers)
        return response


# get current game state
def getGame(game: Game):
    game_id = game.get("game_id")
    user_id = game.get("user_id")
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/state") as client:
        response = client.get(f"users/{user_id}/game/{game_id}", headers=headers)
        return response


# check if user has guesses remaining in this game
def isValidGame(game: Game):
    game_id = game.game_id
    user_id = game.user_id
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
        return response


# post user's guess to game
def add_guess(game: Game, guess: str):
    # load game data
    game_id = game.get("game_id")
    user = game.get("user_id")
    # build Guess model to pass to game_state service
    current_guess = Guess(user_id=user, guess=guess).json()
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/state") as client:
        response = client.post(
            f"/game/{game_id}/new", data=current_guess, headers=headers
        )
        return response


# mark won game as finished
def markGameComplete(game: Game):
    # load game data
    user_id = game.get("user_id")
    game_id = game.get("game_id")
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/state") as client:
        response = client.put(f"/users/{user_id}/game/{game_id}", headers=headers)
        return response


# update user stats if this game is finished
def updateStats(game: Game):
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/statistics") as client:
        response = client.post(f"/users/", json=game, headers=headers)
        return response


# get user stats
def getStats(user_id: str):
    headers = {"content-type": "application/json"}
    with httpx.Client(base_url="http://localhost:9999/api/statistics") as client:
        response = client.get(f"/users/{user_id}/stats", headers=headers)
        return response


settings = Settings()
app = FastAPI(root_path="/api/bff", openapi_url=settings.openapi_url)


@app.post("/game/new")
# NEW GAME workflow
# input: username
# output: game state of this game
# error conditions:
#   - game id already exists (conflict)
def new_game(username: User):
    # game_id test value - when not using default (today)
    # test_gameid = 20220221
    # get user_id
    user = getUser(username.username)
    # print values for getUser response
    print("getUser():\n\t", user, "\n")
    user_text = json.loads(user.text)
    user = user_text.get("user_id")
    # create new game object using user and default game_id
    game = Game(user_id=user).json()
    # test another day using test game_id
    # game = Game(user_id=user, game_id=test_gameid).json()
    # pass new game object and create new game
    # store/print response in "new_game" for debugging
    response = create_game(game)
    return response.json()


# NEW GUESS Workflow
# input: user_id (pick one)
# output:
# error conditions:
#   - game doesn't exist
#   - game has ended
#   - word isn't valid
@app.post("/game/{game_id}")
def new_guess(game_id: int, guess: Guess):
    # get user from guess request body
    user = guess.user_id
    # create game object
    game = Game(user_id=user, game_id=game_id)
    # get guess string from guess request body
    current_guess = guess.guess
    isCorrect = False
    isWordValid = False
    isGameValid = False

    # check if game is valid
    print("\nisValidGame():")
    if isValidGame(game):
        isGameValid = True

    # check if word is valid
    print("\nisValidWord():")
    if isValidWord(current_guess):
        isWordValid = True
    else:
        # raise 400 error - bad request and get remaining guesses from game state
        game_state = getGame(json.loads(game.json()))
        game_text = json.loads(game_state.text)
        guess_remaining = game_text.get("remaining")
        invalid_body = {"status": "invalid", "remaining": guess_remaining}
        invalid_response = Response(
            status_code=400,
            content=json.dumps(invalid_body),
            media_type="application/json",
        )
        print(invalid_response.status_code)
        print(json.dumps(invalid_body))
        return invalid_response

    # add new guess to game
    if (isWordValid) and (isGameValid):
        print("\nadd_guess():")
        add_guess(json.loads(game.json()), current_guess)

        # check if the guess is correct from the response
        print("\ncheck_guess():")
        check = check_guess(current_guess, game_id)
        check_text = json.loads(check.text)
        check_status = check_text.get("status")
        if check_status == "correct":
            isCorrect = True
            markGameComplete(json.loads(game.json()))
        else:
            return check.json()

        # get game state
        game_state = getGame(json.loads(game.json()))
        game_text = json.loads(game_state.text)
        game_status = game_text.get("status")
        # check if game is finished
        # if won or lost, get/set number of guesses and update stats.
        if game_status == "finished":
            num_guesses = len(game_text.get("guesses"))
            updated_game = Game(
                user_id=user, game_id=game_id, won=isCorrect, guesses=num_guesses
            )
            updateStats(json.loads(updated_game.json()))
            # get updated stats
            return getStats(user).json()


# test new game() for endpoint
# user1 = "christina22"
# new_game(user1)


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
