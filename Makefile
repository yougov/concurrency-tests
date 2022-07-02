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
