install:
	cd backend && pip install -r requirements.txt
test:
	cd backend && pytest -q
lint:
	cd backend && ruff check app tests
demo:
	curl -X POST http://localhost:8000/api/v1/demo/seed
