#!/bin/bash
# Lab Platform Orchestrator Startup Script

echo "Lab Platform Orchestrator Startup"
echo "================================="

# Set the working directory to the orchestrator directory
cd /Users/farahorfaly/Desktop/lab_platform/infra/orchestrator

# Create .env file with MQTT settings if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file with MQTT settings..."
    cat > .env << EOF
# Lab Platform Orchestrator Configuration

# MQTT Broker Settings
MQTT_HOST=192.168.1.63
MQTT_PORT=1883
MQTT_USERNAME=tasmota
MQTT_PASSWORD=1234

# Orchestrator Settings
HOST=0.0.0.0
PORT=8000

# Service Settings
TZ=UTC
LOG_LEVEL=INFO

# Features Directory (pointing to the features folder in the project)
FEATURES_PATH=/Users/farahorfaly/Desktop/lab_platform/features

# Production Settings
ORCHESTRATOR_PORT=8000
EOF
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e . --quiet
echo "✓ Dependencies installed"

# Show configuration
echo ""
echo "Configuration:"
echo "  MQTT Host: 192.168.1.63:1883"
echo "  Orchestrator: http://0.0.0.0:8000"
echo "  Features Path: /Users/farahorfaly/Desktop/lab_platform/features"
echo ""

# Start the orchestrator
echo "Starting orchestrator..."
echo "Access the web interface at: http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

python -m lab_orchestrator.host
