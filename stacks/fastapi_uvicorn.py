import asyncio
import time

import httpx
from fastapi import FastAPI

import orjson as json
from fastapi.responses import ORJSONResponse

from stacks.base import JsonDict, URLS


app = FastAPI()
client = httpx.AsyncClient()


async def fetch_data(url: str) -> JsonDict:
    response = await client.get(url)
    return json.loads(response.content)


@app.get('/data', response_class=ORJSONResponse)
async def data() -> list[JsonDict]:
    start = time.time()
    coroutines = [fetch_data(url) for url in URLS]
    gathered_data = await asyncio.gather(*coroutines)
    elapsed = time.time() - start
    print('Took', elapsed, 'seconds to gather data')
    return gathered_data
