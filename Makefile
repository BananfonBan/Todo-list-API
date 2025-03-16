# env
MESSAGE_FOR_MIGRATION="Default message"
APP_MODULE=src.app:app
HOST=0.0.0.0
PORT=8000

# Install dependencies
install:
	pip install -r requirements.txt


# Run app
run: test
	alembic upgrade head  # Use migration before starting
	uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT)


# Run alembic migration
migrate:
	alembic upgrade head


test:
	pytest --cov

test-vv:
	pytest --cov -vv


start-debug: test
	uvicorn src.app:app --reload


automigraiton:
	alembic revision --autogenerate -m $(MESSAGE_FOR_MIGRATION)
