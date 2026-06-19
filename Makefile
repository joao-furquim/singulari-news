.PHONY: lint format test test-frontend test-integration test-all deps up down

lint:
	cd backend && poetry run black --check . ../agent/
	cd backend && poetry run flake8 . ../agent/
	cd consumer && npx eslint src/
	cd consumer && npx prettier --check src/

format:
	cd backend && poetry run black . ../agent/
	cd backend && poetry run isort . ../agent/
	cd consumer && npx prettier --write src/

test:
	cd backend && poetry run pytest tests/ -v --ignore=tests/integration
	cd consumer && npx tsc --noEmit

test-frontend:
	cd frontend && npm test

test-integration:
	cd backend && poetry run pytest tests/integration/ -v

test-all:
	$(MAKE) test
	$(MAKE) test-frontend
	$(MAKE) test-integration

deps:
	cd backend && poetry export -f requirements.txt --output requirements.txt --without-hashes --only main

up:
	docker-compose up --build

down:
	docker-compose down -v
