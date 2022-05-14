import asyncio
import httpx
import json

from answers import app as answer_service
from words import app as word_service
from stats import app as stats_service
from game_state import app as game_state_service


# TODO: get user_id from stats service
async def getUser():
    async with httpx.AsyncClient(
        app=stats_service, base_url="http://120.0.0.1:9999"
    ) as client:
        r = await client.get("/users/christina22")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: check if user has guesses remaining in this game
async def isValidGame():
    async with httpx.AsyncClient(
        app=game_state_service, base_url="http://120.0.0.1:9999"
    ) as client:
        r = await client.get("/game/")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: check if word is valid guess
async def isValidWord():
    async with httpx.AsyncClient(
        app=word_service, base_url="http://120.0.0.1:9999"
    ) as client:
        r = await client.get("/word/guess")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: check if valid guess is correct answer
async def check_guess():
    async with httpx.AsyncClient(
        app=answer_service, base_url="http://120.0.0.1:9999"
    ) as client:
        r = await client.get("/check/soaps")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: update user stats if this game is finished
async def updateStats():
    async with httpx.AsyncClient(
        app=stats_service, base_url="http://120.0.0.1:9999"
    ) as client:
        r = await client.post("/users/b07ecefc-a928-4b3a-a418-cb8930dd93b4")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# TODO: return user stats
async def getStats():
    async with httpx.AsyncClient(
        app=stats_service, base_url="http://120.0.0.1:9999"
    ) as client:
        r = await client.get("/users/b07ecefc-a928-4b3a-a418-cb8930dd93b4/stats")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# define tasks to run concurrently
# async def main():

# run concurrently
# asyncio.run(main())

# test async
asyncio.run(getUser())
asyncio.run(getStats())
asyncio.run(check_guess())
