#!/bin/bash
# Deploy Lab Platform Device Agent to Raspberry Pi

RPI_HOST="192.168.1.142"
RPI_USER="pi"
DEPLOY_DIR="/home/pi/lab_platform"

echo "Lab Platform Device Agent Deployment"
echo "===================================="
echo "Target: ${RPI_USER}@${RPI_HOST}"
echo "Deploy to: ${DEPLOY_DIR}"
echo ""

# Create deployment package
echo "Creating deployment package..."
rm -rf deploy_package
mkdir -p deploy_package

# Copy device agent
cp -r device-agent deploy_package/

# Copy features (modules only, plugins run on orchestrator)
mkdir -p deploy_package/features/modules
cp -r features/modules/* deploy_package/features/modules/ 2>/dev/null || true

# Copy shared utilities
cp -r shared deploy_package/ 2>/dev/null || true

# Create setup script for RPi
cat > deploy_package/setup_agent.sh << 'EOF'
#!/bin/bash
# Setup Lab Platform Device Agent on Raspberry Pi

echo "Setting up Lab Platform Device Agent..."

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-dev

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python packages
echo "Installing Python dependencies..."
cd device-agent
pip install -e . --quiet
cd ..

# Install pyserial for projector module
pip install pyserial --quiet

echo "✓ Setup complete"
EOF

# Create start script for RPi
cat > deploy_package/start_agent.sh << 'EOF'
#!/bin/bash
# Start Lab Platform Device Agent

echo "Starting Lab Platform Device Agent..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables if .env doesn't exist
if [ ! -f device-agent/.env ]; then
    export DEVICE_ID=rpi-lab-01
    export DEVICE_LABELS=lab,rpi,ndi,projector
    export MQTT_HOST=192.168.1.63
    export MQTT_PORT=1883
    export MQTT_USERNAME=tasmota
    export MQTT_PASSWORD=1234
    export HEARTBEAT_INTERVAL_S=10
    export FEATURES_PATH=/home/pi/lab_platform/features
    export LOG_LEVEL=INFO
fi

# Start the agent
cd device-agent
python -m lab_agent.agent
EOF

# Make scripts executable
chmod +x deploy_package/setup_agent.sh
chmod +x deploy_package/start_agent.sh

echo "✓ Deployment package created"

# Deploy to Raspberry Pi
echo ""
echo "Deploying to Raspberry Pi..."
echo "You will be prompted for the pi user password"

# Create directory on RPi
ssh ${RPI_USER}@${RPI_HOST} "mkdir -p ${DEPLOY_DIR}"

# Copy files
scp -r deploy_package/* ${RPI_USER}@${RPI_HOST}:${DEPLOY_DIR}/

# Run setup on RPi
ssh ${RPI_USER}@${RPI_HOST} "cd ${DEPLOY_DIR} && bash setup_agent.sh"

echo ""
echo "✓ Deployment complete!"
echo ""
echo "To start the agent on the Raspberry Pi:"
echo "  ssh ${RPI_USER}@${RPI_HOST}"
echo "  cd ${DEPLOY_DIR}"
echo "  ./start_agent.sh"
echo ""
echo "To run as a service, create /etc/systemd/system/lab-agent.service"

# Cleanup
rm -rf deploy_package
