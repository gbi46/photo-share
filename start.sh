#!/bin/bash
set -e

echo "Waiting for Postgres..."
./wait-for-it.sh db:5432 --timeout=30 --strict

echo "Running Alembic migrations..."
alembic revision --autogenerate -m "Init" || echo "Revision already exists"
alembic upgrade head

echo "Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8002 --reload
