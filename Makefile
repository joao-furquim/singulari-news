.PHONY: lint format test deps up down

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
	cd backend && poetry run pytest tests/ -v
	cd consumer && npx tsc --noEmit

deps:
	cd backend && poetry export -f requirements.txt --output requirements.txt --without-hashes --only main

up:
	docker-compose up --build

down:
	docker-compose down -v
