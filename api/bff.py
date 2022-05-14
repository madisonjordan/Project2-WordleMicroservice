import asyncio
import httpx
import json

from answers import app as answers


async def main():
    async with httpx.AsyncClient(
        app=answers, base_url="http://120.0.0.1:9999"
    ) as client:
        r = await client.get("/check/forge")
        print(r.status_code)
        print(json.dumps(json.loads(r.text), indent=4))


asyncio.run(main())
