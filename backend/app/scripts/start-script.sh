#!/bin/sh

DB_HOST=$1
DB_PORT=$2
TIMEOUT=180  # Max wait time in seconds
START_TIME=$(date +%s)  # Capture start time

echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT (Timeout: $TIMEOUT seconds)..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
  CURRENT_TIME=$(date +%s)  # Get current time
  ELAPSED_TIME=$((CURRENT_TIME - START_TIME))  # Calculate elapsed time

  echo "Still waiting... ($ELAPSED_TIME sec elapsed)"
  if [ "$ELAPSED_TIME" -ge "$TIMEOUT" ]; then
    echo "Error: Timeout reached! PostgreSQL did not start in $TIMEOUT seconds."
    exit 1  # Exit with failure
  fi
done



echo "PostgreSQL is up! Starting application..."
# Change to the app directory before running uvicorn
#cd app 
#python3 main.py
uvicorn main:app --host 0.0.0.0 --port 8000
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "Error: Application failed to start."
  exit 1
fi