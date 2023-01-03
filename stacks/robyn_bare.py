#!/usr/bin/env python3

import asyncio
import time
from os import getenv

import orjson as json
from aiohttp import ClientSession
from robyn import Robyn

from stacks.base import JsonDict, URLS


PORT = int(getenv('PORT', 8000))


app = Robyn(__file__)


async def fetch_data(url: str) -> JsonDict:
    async with ClientSession() as session:
        async with session.get(url) as response:
            return json.loads(await response.read())


@app.get('/data')
async def h(request):
    start = time.time()
    coroutines = [fetch_data(url) for url in URLS]
    gathered_data = await asyncio.gather(*coroutines)
    elapsed = time.time() - start
    print('Took', elapsed, 'seconds to gather data')
    return {'data': gathered_data}


if __name__ == '__main__':
    app.start(url='0.0.0.0', port=PORT)
