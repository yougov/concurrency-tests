#!/usr/bin/env python3
import asyncio
import time
from os import getenv

import orjson as json
from aiohttp import ClientSession, web
from uvloop import EventLoopPolicy

from stacks.base import JsonDict, URLS


PORT = int(getenv('PORT', 8000))


routes = web.RouteTableDef()


async def fetch_data(url: str) -> JsonDict:
    async with ClientSession() as session:
        async with session.get(url) as response:
            return json.loads(await response.read())


@routes.get('/data')
async def data(request: web.Request) -> web.Response:
    start = time.time()
    coroutines = [fetch_data(url) for url in URLS]
    gathered_data = await asyncio.gather(*coroutines)
    elapsed = time.time() - start
    print('Took', elapsed, 'seconds to gather data')
    return web.Response(
        body=json.dumps(gathered_data),
        headers={
            'Content-Type': 'application/json',
        },
    )


app = web.Application()
app.add_routes(routes)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(EventLoopPolicy())
    web.run_app(app, host='0.0.0.0', port=PORT)
