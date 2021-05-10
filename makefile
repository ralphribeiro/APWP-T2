build:
	docker-compose build

up:
	docker-compose up -d

tests: up
	docker-compose run --rm --no-deps --entrypoint="python3 -m pytest" api /tests/unidade /tests/integracao tests/ponta-a-ponta

unit-tests:
	docker-compose run --rm --no-deps --entrypoint="python3 -m pytest" api /tests/unidade

integration-tests: up
	docker-compose run --rm --no-deps --entrypoint="python3 -m pytest" api /tests/integracao

e2e-tests: up
	docker-compose run --rm --no-deps --entrypoint="python3 -m pytest" api /tests/ponta-a-ponta

e2e-tests-v-s: up
	docker-compose run --rm --no-deps --entrypoint="python3 -m pytest" api /tests/ponta-a-ponta	-v -s

logs:
	docker-compose logs --tail=25 api

down:
	docker-compose down --remove-orphans

all: down build up test