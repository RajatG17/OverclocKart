#!/bin/sh

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting Flask server..."
exec python app.py
