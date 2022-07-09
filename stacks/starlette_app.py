import asyncio
import time

import orjson as json
from aiohttp import ClientSession
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route

from stacks.base import JsonDict, URLS


async def fetch_data(url: str, session: ClientSession) -> JsonDict:
    async with session.get(url) as response:
        return json.loads(await response.read())


async def data(request):
    start = time.time()
    async with ClientSession() as session:
        coroutines = [fetch_data(url, session) for url in URLS]
        gathered_data = await asyncio.gather(*coroutines)
    elapsed = time.time() - start
    print('Took', elapsed, 'seconds to gather data')

    return Response(json.dumps(gathered_data), headers={
        'Content-Type': 'application/json',
    })


app = Starlette(routes=[
    Route('/data', data),
])
