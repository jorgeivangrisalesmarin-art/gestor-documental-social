.PHONY: dev test lint install clean

install:
	pip install -r api/requirements.txt

dev:
	cd api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd api && pytest -v

lint:
	cd api && flake8 app tests --max-line-length=100 || echo "Linter ejecutado"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
