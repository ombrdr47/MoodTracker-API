#!/bin/sh

# Activate virtual environment
source venv/bin/activate

# Check for errors in each command
flask db upgrade || exit 1
flask translate compile || exit 1

# Start Gunicorn with explicit Python interpreter
exec gunicorn -b :5000 --access-logfile - --error-logfile - "mood_tracker:app"
