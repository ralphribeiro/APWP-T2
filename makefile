build:
	docker-compose build

up:
	docker-compose up -d

tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unidade /tests/integracao tests/ponta-a-ponta

unit-tests:
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unidade

integration-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/integracao

e2e-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/ponta-a-ponta

logs:
	docker-compose logs --tail=25 api

down:
	docker-compose down --remove-orphans

all: down build up test