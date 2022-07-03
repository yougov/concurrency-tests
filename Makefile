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

# Applications
run-uwsgi:
	uwsgi stacks/uwsgi.ini

run-fastapi:
	uvicorn --loop=uvloop --http=httptools --ws=none --host=0.0.0.0 --port=8102 stacks.fastapi_uvicorn:app
