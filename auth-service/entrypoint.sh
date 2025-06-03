#!/bin/sh

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting Auth [uvicorn]..."
exec uvicorn main:app --host 0.0.0.0 --port 5003
