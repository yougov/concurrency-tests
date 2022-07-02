from os import getenv
from typing import Any


N_FILES = 20
NGINX_BASE_URL = getenv('NGINX_BASE_URL', 'http://nginx')


URLS = [
    f'{NGINX_BASE_URL}/{i}.json' for i in range(N_FILES)
]


JsonDict = dict[str, Any]
