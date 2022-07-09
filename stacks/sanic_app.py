import asyncio
import time
from os import getenv
from typing import Any

import orjson as json
from aiohttp import ClientSession
from sanic import Sanic
from sanic.response import HTTPResponse, json as json_response
from uvloop import EventLoopPolicy

from stacks.base import JsonDict, URLS


PORT = int(getenv('PORT', 8000))


asyncio.set_event_loop_policy(EventLoopPolicy())
app = Sanic('SanicApp')


async def fetch_data(url: str, session: ClientSession) -> JsonDict:
    async with session.get(url) as response:
        return json.loads(await response.read())


def dumps(value: Any) -> str:
    return json.dumps(value).decode('utf-8')


@app.get('/data')
async def data(request) -> HTTPResponse:
    start = time.time()
    async with ClientSession() as session:
        coroutines = [fetch_data(url, session) for url in URLS]
        gathered_data = await asyncio.gather(*coroutines)
    elapsed = time.time() - start
    print('Took', elapsed, 'seconds to gather data')
    return json_response(gathered_data, dumps=dumps)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
