#!/usr/bin/env python3

import datetime as dt
import json
import random
from pathlib import Path


PROJECT_PATH = Path(__file__).parent.parent.absolute()
FIXTURES = PROJECT_PATH / 'fixtures'


N_FILES = 100
N_ITEMS = 10000


def date_to_int(date: dt.date) -> int:
    return int(date.strftime('%Y%m%d'))


def main() -> None:
    start_date = dt.date(2020, 1, 1)
    for file_i in range(N_FILES):
        file = FIXTURES / f'{file_i}.json'
        print('Creating file', file)
        data = {
            'columns': ['date', 'foo', 'bar', 'baz'],
            'rows': [
                [
                    date_to_int(start_date + dt.timedelta(days=i)),
                    random.random(),
                    random.random(),
                    random.random(),
                ] for i in range(N_ITEMS)
            ]
        }
        file = FIXTURES / f'{file_i}.json'
        with file.open('w') as f:
            json.dump(data, f)


if __name__ == '__main__':
    main()
