# Lab Platform Setup Summary

## ✅ Completed Tasks

### 1. System Architecture Setup
- **Orchestrator** (This Device): Controls and coordinates all devices
- **Device Agent** (Raspberry Pi 192.168.1.142): Executes commands and runs modules
- **MQTT Broker** (192.168.1.63:1883): Communication hub between components

### 2. Code Optimization
- ✅ Removed 7 unused files from orchestrator (dead_letter, deduplication, retry, middleware, health, metrics, schema)
- ✅ Simplified NDI plugin - removed local discovery, focused on remote device control
- ✅ Simplified Projector plugin - cleaned up API endpoints
- ✅ Fixed all device_id validation in API endpoints

### 3. Configuration Files Created

#### For Orchestrator (This Device)
- `infra/orchestrator/.env` - MQTT settings configured
- `start_orchestrator.sh` - Quick start script

#### For Device Agent (Raspberry Pi)
- `device-agent/config.yaml` - Device configuration with modules
- `device-agent/.env` - Environment variables
- `lab-agent.service` - Systemd service file

### 4. Deployment Tools
- `deploy_to_rpi.sh` - Automated deployment to Raspberry Pi
- `test_system.py` - System verification script
- `DEPLOYMENT.md` - Complete deployment guide

## 🚀 Quick Start

### On This Device (Orchestrator)
```bash
# Start the orchestrator
./start_orchestrator.sh

# Access web interface
open http://localhost:8000
```

### On Raspberry Pi (Device Agent)
```bash
# Deploy to Raspberry Pi
./deploy_to_rpi.sh

# Or manually SSH and start
ssh pi@192.168.1.142
cd /home/pi/lab_platform
./start_agent.sh
```

### Test the System
```bash
# Run system test
python test_system.py
```

## 📋 Key Features

### NDI Module
- Start/stop NDI viewer
- Set input source
- Record streams
- Process management

### Projector Module  
- Power control (on/off)
- Input selection (HDMI1/HDMI2)
- Navigation controls
- Image adjustments (keystone, shift)

## 🔧 MQTT Communication

### Topic Structure
```
/lab/device/{device_id}/cmd         → Send commands to device
/lab/device/{device_id}/evt         → Receive device events
/lab/device/{device_id}/status      → Device online/offline status
/lab/device/{device_id}/{module}/cmd → Module-specific commands
/lab/orchestrator/registry           → Device registry
```

### Message Format
```json
{
  "req_id": "unique-id",
  "actor": "api|orchestrator|user",
  "action": "command-name",
  "params": {},
  "ts": "2024-01-01T00:00:00Z"
}
```

## 🌐 API Endpoints

### Device Management
- `GET /api/registry` - List all devices
- `POST /api/devices/{device_id}/modules` - Add module
- `DELETE /api/devices/{device_id}/modules/{module}` - Remove module

### NDI Control
- `POST /api/ndi/start` - Start NDI viewer
- `POST /api/ndi/stop` - Stop NDI viewer  
- `POST /api/ndi/input` - Set input source
- `POST /api/ndi/record/start` - Start recording
- `POST /api/ndi/record/stop` - Stop recording

### Projector Control
- `POST /api/projector/power` - Power on/off
- `POST /api/projector/input` - Select input
- `POST /api/projector/navigate` - Navigation
- `POST /api/projector/adjust` - Adjustments

## 📁 Project Structure

```
lab_platform/
├── infra/orchestrator/     # Orchestrator service
│   ├── src/lab_orchestrator/
│   └── .env               # MQTT configuration
├── device-agent/          # Device agent for RPi
│   ├── src/lab_agent/
│   └── config.yaml        # Device configuration
├── features/
│   ├── plugins/           # Orchestrator plugins
│   │   ├── ndi/
│   │   └── projector/
│   └── modules/           # Device modules
│       ├── ndi/
│       └── projector/
└── Deployment files:
    ├── start_orchestrator.sh
    ├── deploy_to_rpi.sh
    ├── lab-agent.service
    ├── test_system.py
    └── DEPLOYMENT.md
```

## ⚠️ Important Notes

1. **MQTT Broker** must be running at 192.168.1.63:1883
2. **Raspberry Pi** must have network access to MQTT broker
3. **Modules** only run on device agents (RPi), not orchestrator
4. **Plugins** only run on orchestrator, not device agents

## 🔍 Troubleshooting

### Check MQTT Connection
```bash
mosquitto_sub -h 192.168.1.63 -p 1883 -u tasmota -P 1234 -t '/lab/#' -v
```

### Check Device Agent Logs (on RPi)
```bash
sudo journalctl -u lab-agent -f
```

### Check Orchestrator Logs
Look at console output when running `./start_orchestrator.sh`

## ✨ Next Steps

1. **Start the orchestrator** on this device
2. **Deploy and start the agent** on Raspberry Pi
3. **Test the system** using test_system.py
4. **Access web UI** at http://localhost:8000

The system is now ready for full control of the device agent and modules via MQTT!
