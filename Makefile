.PHONY: dev api web test lint seed check

# Desarrollo local rápido (API con sqlite; sin docker)
dev: api

api:
	cd api && ../.venv/bin/uvicorn app.main:app --reload --port 8000

web:
	cd web && npm run dev

test:
	cd api && ../.venv/bin/python -m pytest -q

lint:
	cd api && ../.venv/bin/ruff check app tests

check: lint test

# Con docker (Postgres + API + Web)
up:
	docker compose up --build -d

down:
	docker compose down
