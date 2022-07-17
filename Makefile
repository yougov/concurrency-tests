install:
	pip install -r requirements.txt

dependency-compile:
	pip-compile
	$(MAKE) dependency-sync

dependency-sync:
	pip-sync

up:
	cd stacks/rustapp && cargo build --release
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
	uvicorn --loop=uvloop --http=httptools --ws=none --host=0.0.0.0 --port=${PORT} stacks.fastapi_uvicorn:app

run-fastapi-hypercorn:
	hypercorn --worker-class=uvloop --bind=0.0.0.0:${PORT} stacks.fastapi_uvicorn:app

run-aiohttp:
	python3 stacks/aiohttp_multi_loop.py

run-sanic-direct:
	python3 stacks/sanic_app.py

run-sanic-asgi:
	uvicorn --loop=uvloop --http=httptools --ws=none --host=0.0.0.0 --port=${PORT} stacks.sanic_app:app

run-starlette-uvicorn:
	uvicorn --loop=uvloop --http=httptools --ws=none --host=0.0.0.0 --port=${PORT} stacks.starlette_app:app

run-aiohttp-gunicorn:
	gunicorn stacks.aiohttp_multi_loop:app --bind=0.0.0.0:${PORT} --worker-class=aiohttp.GunicornUVLoopWebWorker --workers=4

run-aiohttp-uwsgi:
	uwsgi stacks/uwsgi-aiohttp.ini

run-rust-app:
	./stacks/rustapp/target/release/rustapp
