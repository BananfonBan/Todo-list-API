start:
	uvicorn src.app:app

start-debug:
	uvicorn src.app:app --reload

automigraiton:
	alembic revision --autogenerate -m "$(MESSAGE_FOR_MIGRATION)"