#!/usr/bin/env python3
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
    final_data: list[JsonDict] = []
    with ThreadPoolExecutor(len(URLS)) as executor:
        futures: list[Future] = [
            executor.submit(fetch_data, url) for url in URLS
        ]
        for future in as_completed(futures):
            final_data.append(future.result())

    response = make_response(json.dumps(final_data))
    response.headers['Content-Type'] = 'application/json'
    return response
