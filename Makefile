# env
MESSAGE_FOR_MIGRATION="Default message"
APP_MODULE=src.app:app
HOST=0.0.0.0
PORT=8000

# Run app
run:
	alembic upgrade head  # Use migration before starting
	uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT)


# Run alembic migration
migrate:
	alembic upgrade head


start-debug:
	uvicorn src.app:app --reload


automigraiton:
	alembic revision --autogenerate -m $(MESSAGE_FOR_MIGRATION)
