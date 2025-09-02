# Lab Platform

A modular, distributed platform for managing laboratory devices and workflows. The platform provides a clean separation between infrastructure, device agents, and pluggable features.

## Architecture Overview

```
lab_platform/                    # Main umbrella repository
├── infra/                      # Infrastructure components
│   ├── docker-compose.yaml    # EMQX, Postgres, Orchestrator
│   └── orchestrator/           # Central coordination service
├── device-agent/               # Edge device communication
├── features/                   # Pluggable modules and plugins
│   ├── modules/               # Device-side modules (e.g., NDI)
│   └── plugins/               # Orchestrator-side plugins
└── env.example                # Environment configuration template
```

## Components

### 1. Infrastructure (`infra/`)

The infrastructure layer runs as a server stack and includes:

- **EMQX**: MQTT broker for device communication
- **PostgreSQL**: Database for persistent storage
- **Orchestrator**: Central coordination service with web UI and API

The orchestrator is a FastAPI application that:
- Manages device registry and status
- Provides plugin system for extensible functionality
- Offers web UI for monitoring and control
- Handles resource locking and scheduling

### 2. Device Agent (`device-agent/`)

The device agent runs on edge devices (like Raspberry Pi) and:
- Connects to the MQTT broker
- Loads modules dynamically from `features/`
- Publishes device metadata and status
- Handles commands from the orchestrator
- Manages module lifecycle and configuration

### 3. Features (`features/`)

Features are the pluggable components that extend the platform:

- **Modules** (`features/modules/`): Run on device agents
- **Plugins** (`features/plugins/`): Run on the orchestrator

Each feature has a manifest file describing its capabilities and configuration.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for development)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd lab_platform
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start infrastructure**:
   ```bash
   cd infra
   docker-compose up -d
   ```

4. **Access the web UI**:
   - Orchestrator: http://localhost:8000
   - EMQX Dashboard: http://localhost:18083 (admin/public)

### Setting up a Device Agent

1. **Install the device agent**:
   ```bash
   cd device-agent
   pip install -e .
   ```

2. **Configure the agent**:
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your device settings
   ```

3. **Run the agent**:
   ```bash
   lab-agent
   ```

## Development

### Project Structure

```
lab_platform/
├── infra/orchestrator/
│   ├── src/lab_orchestrator/     # Python package
│   │   ├── host.py              # Main FastAPI application
│   │   ├── plugin_api.py        # Plugin interface
│   │   └── services/            # Core services
│   ├── pyproject.toml           # Package configuration
│   └── Dockerfile               # Container image
├── device-agent/
│   ├── src/lab_agent/           # Python package
│   │   ├── agent.py             # Main agent implementation
│   │   ├── base.py              # Module base class
│   │   └── common.py            # Shared utilities
│   └── pyproject.toml           # Package configuration
└── features/
    ├── modules/ndi/             # NDI device module
    │   ├── manifest.yaml        # Module metadata
    │   └── ndi_module.py        # Module implementation
    └── plugins/ndi/             # NDI orchestrator plugin
        ├── manifest.yaml        # Plugin metadata
        └── ndi_plugin.py        # Plugin implementation
```

### Adding New Features

#### Creating a Device Module

1. Create directory: `features/modules/your_module/`
2. Add `manifest.yaml` with module metadata
3. Implement module class extending `lab_agent.base.Module`
4. The agent will load it automatically

#### Creating an Orchestrator Plugin

1. Create directory: `features/plugins/your_plugin/`
2. Add `manifest.yaml` with plugin metadata
3. Implement plugin class extending `lab_orchestrator.plugin_api.OrchestratorPlugin`
4. The orchestrator will load it automatically

### MQTT Topics

The platform uses a structured MQTT topic hierarchy:

```
/lab/
├── device/{device_id}/
│   ├── meta                    # Device metadata (retained)
│   ├── status                  # Device status (retained)
│   ├── cmd                     # Device commands
│   ├── evt                     # Device events
│   └── {module}/
│       ├── cmd                 # Module commands
│       ├── cfg                 # Module configuration
│       ├── status              # Module status (retained)
│       └── evt                 # Module events
├── orchestrator/
│   ├── registry                # Device registry (retained)
│   └── {module}/
│       ├── cmd                 # Plugin commands
│       └── evt                 # Plugin events
```

## Example: NDI Feature

The platform includes an NDI (Network Device Interface) feature as an example:

- **Module** (`features/modules/ndi/`): Manages NDI viewers and recording on devices
- **Plugin** (`features/plugins/ndi/`): Provides web UI and API for NDI control

### NDI Module Capabilities

- Start/stop NDI viewers
- Change input sources
- Record NDI streams
- Process and environment management

### NDI Plugin Features

- Web UI for device control
- REST API endpoints
- Device reservation system
- Command scheduling
- Dynamic source discovery

## Configuration

### Environment Variables

See `env.example` for all available configuration options:

- **MQTT Settings**: Broker connection and credentials
- **Database Settings**: PostgreSQL configuration
- **Service Ports**: Exposed port mappings
- **Security Settings**: Passwords and tokens

### Device Agent Configuration

The device agent uses `config.yaml`:

```yaml
device_id: "lab-device-01"
labels: ["example", "lab"]
mqtt:
  host: "localhost"
  port: 1883
  username: "mqtt"
  password: "public"
heartbeat_interval_s: 10
modules: {}  # Loaded dynamically from features/
```

## API Reference

### Orchestrator API

- `GET /api/registry` - Get device registry
- `DELETE /api/registry/devices/{device_id}` - Remove device
- `GET /api/{module}/*` - Module-specific endpoints

### Web UI

- `/` - Main dashboard
- `/ui/devices` - Device management
- `/ui/{module}` - Module-specific UIs

## Monitoring and Logging

- **EMQX Dashboard**: Monitor MQTT traffic and connections
- **Application Logs**: Structured logging from all components
- **Health Checks**: Built-in health monitoring for all services

## Security Considerations

- MQTT authentication and authorization
- Network isolation using Docker networks
- Resource locking to prevent conflicts
- Input validation and sanitization

## Troubleshooting

### Common Issues

1. **Device not appearing in registry**:
   - Check MQTT connection
   - Verify topic structure
   - Check device agent logs

2. **Plugin not loading**:
   - Verify manifest.yaml syntax
   - Check Python import paths
   - Review orchestrator logs

3. **Connection issues**:
   - Verify network connectivity
   - Check firewall settings
   - Confirm service health

### Debug Mode

Enable debug logging by setting environment variables:
```bash
export LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Your License Here]

## Support

For questions and support, please [open an issue](link-to-issues) or contact the development team.
