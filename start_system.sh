#!/bin/bash

# ThreatSenseAI System Startup Script (Dockerized)

echo "=================================================="
echo "   ThreatSenseAI - Dual-Agent Disaster Detection  "
echo "=================================================="

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH."
    exit 1
fi

echo "[1/3] Stopping any running containers..."
docker-compose down

echo "[2/3] Building and Starting Services..."
# Build without cache to ensure new deps are picked up, and run in background
docker-compose up --build -d

echo "[3/3] Waiting for services to stabilize..."
sleep 10

echo "------------------------------------------------"
echo "System is operational via Docker:"
echo "Frontend:      http://localhost:5173"
echo "Auth Service:  http://localhost:8000"
echo "AI Service:    http://localhost:7001"
echo "------------------------------------------------"
echo "Logs (Follow):"
docker-compose logs -f
