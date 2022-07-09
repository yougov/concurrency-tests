import asyncio
import cProfile
import time

from aiohttp import ClientSession
from fastapi import FastAPI

import orjson as json
from fastapi.responses import ORJSONResponse
from fastapi import Response

from stacks.base import JsonDict, PROJECT_PATH, URLS


PROFILING_PATH = PROJECT_PATH / 'profiling'
PROFILING_PATH.mkdir(exist_ok=True)


class ProfilingFastAPI(FastAPI):
    async def __call__(self, scope, receive, send):
        profiler = cProfile.Profile()
        profiler.enable()
        await super().__call__(scope, receive, send)
        profiler.disable()
        profiler.dump_stats(PROFILING_PATH / 'fastapi-request.data')


app = FastAPI()


async def fetch_data(url: str, session: ClientSession) -> JsonDict:
    async with session.get(url) as response:
        return json.loads(await response.read())


@app.get('/data')
async def data():
    start = time.time()
    async with ClientSession() as session:
        coroutines = [fetch_data(url, session) for url in URLS]
        gathered_data = await asyncio.gather(*coroutines)
    elapsed = time.time() - start
    print('Took', elapsed, 'seconds to gather data')
    return Response(
        content=json.dumps(gathered_data),
        headers={
            'Content-Type': 'application/json',
        }
    )
