#!/bin/sh

echo "Starting Order migrations for Order..."
alembic upgrade head

echo "Starting Order service..."
exec python app.py