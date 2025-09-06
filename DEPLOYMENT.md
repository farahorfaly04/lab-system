# Lab Platform Deployment Guide

## Overview

The Lab Platform consists of two main components:
- **Orchestrator**: Runs on your main computer (this device)
- **Device Agent**: Runs on Raspberry Pi (192.168.1.142)

## Architecture

```
┌─────────────────┐         MQTT Broker         ┌──────────────────┐
│   Orchestrator  │◄────── 192.168.1.63 ──────►│   Device Agent   │
│  (This Device)  │         Port: 1883          │  (Raspberry Pi)  │
│                 │                              │  192.168.1.142   │
│   - Plugins:    │                              │   - Modules:     │
│     • NDI       │                              │     • NDI        │
│     • Projector │                              │     • Projector  │
└─────────────────┘                              └──────────────────┘
```

## Prerequisites

### MQTT Broker
- Host: 192.168.1.63
- Port: 1883
- Username: tasmota
- Password: 1234

### On This Device (Orchestrator)
- Python 3.8+
- Git

### On Raspberry Pi (Device Agent)
- Python 3.8+
- SSH access enabled
- Network connectivity to MQTT broker

## Deployment Instructions

### 1. Deploy Orchestrator (This Device)

#### Quick Start
```bash
# Make the script executable
chmod +x start_orchestrator.sh

# Run the orchestrator
./start_orchestrator.sh
```

#### Manual Setup
```bash
# Navigate to orchestrator directory
cd infra/orchestrator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Start orchestrator
python -m lab_orchestrator.host
```

The orchestrator will be available at: http://localhost:8000

### 2. Deploy Device Agent (Raspberry Pi)

#### Automated Deployment
```bash
# Make the deployment script executable
chmod +x deploy_to_rpi.sh

# Deploy to Raspberry Pi (you'll be prompted for password)
./deploy_to_rpi.sh
```

#### Manual Deployment

1. **Copy files to Raspberry Pi:**
```bash
# On this device
scp -r device-agent features/modules shared pi@192.168.1.142:/home/pi/lab_platform/
```

2. **SSH into Raspberry Pi:**
```bash
ssh pi@192.168.1.142
```

3. **Setup on Raspberry Pi:**
```bash
cd /home/pi/lab_platform

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install device agent
cd device-agent
pip install -e .
cd ..

# Install module dependencies
pip install pyserial  # For projector module
```

4. **Configure and Start Agent:**
```bash
# Set environment variables
export DEVICE_ID=rpi-lab-01
export DEVICE_LABELS=lab,rpi,ndi,projector
export MQTT_HOST=192.168.1.63
export MQTT_PORT=1883
export MQTT_USERNAME=tasmota
export MQTT_PASSWORD=1234
export FEATURES_PATH=/home/pi/lab_platform/features

# Start the agent
cd device-agent
python -m lab_agent.agent
```

### 3. Run Device Agent as Service (Raspberry Pi)

1. **Copy service file to Raspberry Pi:**
```bash
scp lab-agent.service pi@192.168.1.142:/tmp/
```

2. **Install service on Raspberry Pi:**
```bash
ssh pi@192.168.1.142

# Install service
sudo cp /tmp/lab-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lab-agent
sudo systemctl start lab-agent

# Check status
sudo systemctl status lab-agent

# View logs
sudo journalctl -u lab-agent -f
```

## Configuration Files

### Orchestrator Configuration
Location: `infra/orchestrator/.env`
```env
MQTT_HOST=192.168.1.63
MQTT_PORT=1883
MQTT_USERNAME=tasmota
MQTT_PASSWORD=1234
HOST=0.0.0.0
PORT=8000
FEATURES_PATH=/Users/farahorfaly/Desktop/lab_platform/features
```

### Device Agent Configuration
Location: `device-agent/config.yaml`
```yaml
device_id: "rpi-lab-01"
labels: ["lab", "rpi", "ndi", "projector"]

mqtt:
  host: "192.168.1.63"
  port: 1883
  username: "tasmota"
  password: "1234"

modules:
  ndi:
    ndi_path: "/usr/local/lib/ndi"
    start_cmd_template: "ndi-viewer {source}"
    log_file: "/tmp/ndi_{device_id}.log"
  
  projector:
    serial_port: "/dev/ttyUSB0"
    baud_rate: 9600
    timeout: 5
```

## Verification

### 1. Check Orchestrator
- Open http://localhost:8000 in your browser
- You should see the Lab Platform dashboard
- Check `/api/registry` for connected devices

### 2. Check Device Agent
On Raspberry Pi:
```bash
# Check if agent is running
ps aux | grep lab_agent

# Check MQTT connection
mosquitto_sub -h 192.168.1.63 -p 1883 -u tasmota -P 1234 -t '/lab/device/+/status' -v
```

### 3. Test Communication

#### From Orchestrator Web UI:
1. Navigate to http://localhost:8000/ui/devices
2. You should see "rpi-lab-01" listed
3. Try sending commands through the UI

#### Using MQTT directly:
```bash
# Send ping command to device
mosquitto_pub -h 192.168.1.63 -p 1883 -u tasmota -P 1234 \
  -t '/lab/device/rpi-lab-01/cmd' \
  -m '{"req_id":"test-1","action":"ping","params":{},"actor":"test"}'

# Listen for response
mosquitto_sub -h 192.168.1.63 -p 1883 -u tasmota -P 1234 \
  -t '/lab/device/rpi-lab-01/evt' -v
```

## API Endpoints

### Orchestrator API

#### Device Management
- `GET /api/registry` - Get all devices and their status
- `DELETE /api/registry/devices/{device_id}` - Remove a device
- `POST /api/devices/{device_id}/modules` - Add module to device
- `DELETE /api/devices/{device_id}/modules/{module_name}` - Remove module

#### NDI Control
- `GET /api/ndi/devices` - List NDI-capable devices
- `POST /api/ndi/start` - Start NDI viewer
- `POST /api/ndi/stop` - Stop NDI viewer
- `POST /api/ndi/input` - Set NDI input source
- `POST /api/ndi/record/start` - Start recording
- `POST /api/ndi/record/stop` - Stop recording

#### Projector Control
- `GET /api/projector/devices` - List projector-capable devices
- `POST /api/projector/power` - Set power state (on/off)
- `POST /api/projector/input` - Set input source (hdmi1/hdmi2)
- `POST /api/projector/navigate` - Send navigation command
- `POST /api/projector/adjust` - Adjust settings (keystone, image shift)

## Troubleshooting

### Orchestrator Issues

1. **Cannot connect to MQTT:**
   - Check MQTT broker is running at 192.168.1.63:1883
   - Verify credentials (tasmota/1234)
   - Check network connectivity: `ping 192.168.1.63`

2. **Plugins not loading:**
   - Check FEATURES_PATH is set correctly
   - Verify plugin manifest.yaml files exist
   - Check logs for import errors

### Device Agent Issues

1. **Agent not connecting:**
   - Verify MQTT settings in config.yaml or environment
   - Check network from RPi: `ping 192.168.1.63`
   - Review agent logs: `journalctl -u lab-agent -f`

2. **Modules not loading:**
   - Check features/modules directory exists
   - Verify module manifest.yaml files
   - Check Python dependencies are installed

3. **Projector not responding:**
   - Check serial device exists: `ls /dev/ttyUSB*`
   - Verify baud rate matches projector settings
   - Check serial permissions: `sudo usermod -a -G dialout pi`

### MQTT Debugging

Monitor all MQTT traffic:
```bash
# Subscribe to all lab platform topics
mosquitto_sub -h 192.168.1.63 -p 1883 -u tasmota -P 1234 -t '/lab/#' -v
```

## Module-Specific Setup

### NDI Module
If using NDI on Raspberry Pi:
1. Install NDI SDK from https://www.ndi.tv/sdk/
2. Set NDI_PATH in config or environment
3. Install any NDI tools (ndi-viewer, ndi-recorder)

### Projector Module
1. Connect projector via USB-to-Serial adapter
2. Identify serial port: `ls /dev/ttyUSB*`
3. Update config.yaml with correct port
4. Ensure user has serial permissions

## Security Notes

1. **MQTT Credentials**: Store in environment variables or .env files
2. **Network Security**: Use firewall rules to restrict MQTT access
3. **Device Access**: Implement proper authentication for production use
4. **Serial Ports**: Limit access to serial devices on Raspberry Pi

## Maintenance

### Logs
- Orchestrator: Check console output or redirect to file
- Device Agent: `/tmp/ndi_rpi-lab-01.log` and `/tmp/projector_rpi-lab-01.log`
- System: `journalctl -u lab-agent`

### Updates
1. Pull latest code from repository
2. Restart services:
   ```bash
   # Orchestrator
   Ctrl+C and restart ./start_orchestrator.sh
   
   # Device Agent (on RPi)
   sudo systemctl restart lab-agent
   ```

## Support

For issues or questions:
1. Check logs for error messages
2. Verify MQTT connectivity
3. Ensure all dependencies are installed
4. Review configuration files for typos
