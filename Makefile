install:
	pip install -r requirements.txt

dependency-compile:
	pip-compile
	$(MAKE) dependency-sync

dependency-sync:
	pip-sync

up:
	docker compose build
	docker compose up

create-fixtures:
	$(eval export PYTHONPATH=${PWD})
	python3 scripts/create-fixtures.py

check-performance:
	$(eval export PYTHONPATH=${PWD})
	python3 scripts/check-performance.py

# Applications
run-uwsgi:
	uwsgi stacks/uwsgi.ini

run-fastapi:
	uvicorn --loop=uvloop --http=httptools --ws=none --host=0.0.0.0 --port=8102 stacks.fastapi_uvicorn:app

run-fastapi-hypercorn:
	hypercorn --worker-class=uvloop --bind=0.0.0.0:${PORT} stacks.fastapi_uvicorn:app

run-aiohttp:
	python3 stacks/aiohttp_multi_loop.py
