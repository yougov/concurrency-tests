#!/usr/bin/env python3
import time

import stacks.async_monkey_patch  # noqa
from concurrent.futures import Future, ThreadPoolExecutor, as_completed

import orjson as json
import requests
from flask import Flask, make_response

from stacks.base import JsonDict, URLS


app = Flask(__name__)


def fetch_data(url: str) -> JsonDict:
    response = requests.get(url)
    response_data = json.loads(response.content)
    return response_data


@app.route('/data')
def data():
    start = time.time()
    final_data: list[JsonDict] = []
    with ThreadPoolExecutor(len(URLS)) as executor:
        for result in executor.map(fetch_data, URLS):
            final_data.append(result)
    elapsed = time.time() - start
    print('Took', elapsed, 'seconds to gather data')

    response = make_response(json.dumps(final_data))
    response.headers['Content-Type'] = 'application/json'
    return response
