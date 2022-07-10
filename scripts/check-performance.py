#!/usr/bin/env python3
import timeit

import requests

from scripts.base import N_ITEMS
from stacks.base import URLS as DATA_URLS


URLS = [
    'http://localhost:8101/data',
    'http://localhost:8102/data',
    'http://localhost:8103/data',
    'http://localhost:8104/data',
    'http://localhost:8105/data',
    'http://localhost:8106/data',
    'http://localhost:8107/data',
    'http://localhost:8108/data',
    'http://localhost:8109/data',
]
N_TIMES = 3
N_REPEATS = 3


def check_performance() -> None:
    print('*** Checking performance ***')
    for url in URLS:
        variables = globals() | locals()
        print('Checking', url)
        timings = timeit.repeat(
            'requests.get(url)', globals=variables,
            number=N_TIMES, repeat=N_REPEATS)
        average = sum(timings) / len(timings)
        print('Average:', average)
        print('Timings:', timings)


def check_correctness():
    print('*** Checking correctness of data ***')
    for url in URLS:
        print('Checking', url)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        assert len(data) == len(DATA_URLS), f'{len(data)} data items'
        for data_item in data:
            columns = data_item['columns']
            rows = data_item['rows']
            assert columns == ['date', 'foo', 'bar', 'baz']
            assert len(rows) == N_ITEMS
        print(url, 'is correct')


if __name__ == '__main__':
    check_correctness()
    check_performance()
