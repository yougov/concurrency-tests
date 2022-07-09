from os import getenv
from pathlib import Path
from typing import Any


N_FILES = 50
NGINX_BASE_URL = getenv('NGINX_BASE_URL', 'http://nginx')
PROJECT_PATH = Path(__file__).parent.parent


URLS = [
    f'{NGINX_BASE_URL}/{i}.json' for i in range(N_FILES)
]


JsonDict = dict[str, Any]
