#!/bin/bash

# Kill ports
lsof -t -i :7001 | xargs kill -9 2>/dev/null
lsof -t -i :8000 | xargs kill -9 2>/dev/null
lsof -t -i :5173 | xargs kill -9 2>/dev/null

# Export Env Vars for Local Run
export DATABASE_URL="postgresql://threatsense:securepassword@localhost:5434/threatsense_db"
export PORT=8000
# Load API keys from .env if needed, but python-dotenv in app.py should handle it if file exists.
# We explicitly export them just in case.
export $(grep -v '^#' .env | xargs)

echo "Starting Postgres DB (if not running)..."
docker start threatsenseai-db-1

echo "Starting Node Backend (Port 8000)..."
cd BackEnd && npm install && npm run dev &
BACKEND_PID=$!

echo "Starting Flask Server (Port 7001)..."
# Using python3 explicitly
cd FlaskServer && python3 app.py &
FLASK_PID=$!

echo "Starting Frontend (Port 5173)..."
cd FrontEnd && npm install && npm run dev &
FRONTEND_PID=$!

echo "Services started locally!"
echo "Backend PID: $BACKEND_PID"
echo "Flask PID: $FLASK_PID"
echo "Frontend PID: $FRONTEND_PID"

wait
