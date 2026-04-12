.PHONY: install run-api run-ui migrate test lint

install:
	python -m pip install -r requirements.txt

run-api:
	uvicorn app.main:app --reload

run-ui:
	streamlit run src/ui/streamlit_app.py

migrate:
	alembic upgrade head

test:
	pytest -q
