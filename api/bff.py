import asyncio
import httpx
import json

from answers import app as answers


async def check_guess():
    async with httpx.AsyncClient(
        app=answers, base_url="http://120.0.0.1:9999"
    ) as client:
        r = await client.get("/check/soaps")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


# async def main():


# asyncio.run(main())
asyncio.run(check_guess())
