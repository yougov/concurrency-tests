#!/usr/bin/env python3
import time
import timeit

import requests


URLS = [
    'http://localhost:8101/data',
    'http://localhost:8102/data',
]


def main() -> None:
    for url in URLS:
        variables = globals() | locals()
        print('Checking', url)
        print(timeit.repeat(
            'requests.get(url)', globals=variables, number=1, repeat=3))


if __name__ == '__main__':
    main()
