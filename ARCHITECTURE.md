# Lab Platform Architecture

This document describes the restructured architecture of the Lab Platform, following the modular design principles outlined in the original requirements.

## Architecture Overview

The Lab Platform is now organized as an umbrella repository with three main components:

```
lab_platform/                           # Main umbrella repository
├── infra/                              # Infrastructure components
│   ├── orchestrator/                   # Central coordination service
│   │   ├── src/lab_orchestrator/       # Python package
│   │   ├── pyproject.toml              # Package definition
│   │   └── Dockerfile                  # Container image
│   └── docker-compose.yaml             # Full stack definition
├── device-agent/                       # Edge device communication
│   ├── src/lab_agent/                  # Python package
│   ├── pyproject.toml                  # Package definition
│   └── config.yaml.example             # Configuration template
├── features/                           # Pluggable modules and plugins
│   ├── modules/ndi/                    # NDI device module
│   └── plugins/ndi/                    # NDI orchestrator plugin
└── README.md                           # Complete documentation
```

## Component Details

### 1. Orchestrator (Infrastructure)

**Location**: `infra/orchestrator/`
**Purpose**: Central coordination service running as part of server infrastructure

**Key Features**:
- FastAPI web application with REST API
- Dynamic plugin loading from `features/plugins/`
- MQTT communication with device agents
- Device registry and resource locking
- Web UI for monitoring and control
- Task scheduling capabilities

**Python Package**: `lab-orchestrator`
- Entry point: `lab-orchestrator` command
- Installable with pip: `pip install -e .`
- Docker image: Built from included Dockerfile

### 2. Device Agent

**Location**: `device-agent/`
**Purpose**: Edge device communication running on Raspberry Pi and similar devices

**Key Features**:
- MQTT client connecting to infrastructure broker
- Dynamic module loading from `features/modules/`
- Device metadata and status publishing
- Command handling and acknowledgment
- Heartbeat and health monitoring

**Python Package**: `lab-agent`
- Entry point: `lab-agent` command
- Installable with pip: `pip install -e .`
- Configuration: `config.yaml`

### 3. Features

**Location**: `features/`
**Purpose**: Pluggable functionality extending both orchestrator and device agents

**Structure**:
- `modules/`: Device-side functionality
- `plugins/`: Orchestrator-side functionality

**Manifest System**: Each feature includes a `manifest.yaml` describing:
- Capabilities and configuration
- API endpoints and UI components
- Dependencies and requirements

## Migration from MVP

The new architecture successfully migrates the working MVP (`ndi_router`) into the clean, modular structure:

### Before (ndi_router)
```
ndi_router/
├── agent/device/               # Device agent code
├── orchestrator/               # Orchestrator code
└── plugins/ndi_plugin/         # NDI plugin
```

### After (lab_platform)
```
lab_platform/
├── infra/orchestrator/         # Clean orchestrator package
├── device-agent/               # Clean agent package
└── features/                   # Separated, reusable features
    ├── modules/ndi/           # Device-side NDI
    └── plugins/ndi/           # Orchestrator-side NDI
```

## Infrastructure Stack

The complete infrastructure runs via Docker Compose:

```yaml
services:
  emqx:         # MQTT broker for device communication
  db:           # PostgreSQL for persistent storage
  orchestrator: # Lab Platform orchestrator service
```

**Benefits**:
- Single command deployment: `docker-compose up -d`
- Automatic service discovery and networking
- Health checks and restart policies
- Volume management for data persistence

## Communication Protocol

### MQTT Topic Hierarchy
```
/lab/
├── device/{device_id}/
│   ├── meta                    # Device metadata (retained)
│   ├── status                  # Device status (retained)
│   ├── cmd                     # Device commands
│   └── {module}/
│       ├── cmd                 # Module commands
│       ├── status              # Module status (retained)
│       └── evt                 # Module events
└── orchestrator/
    ├── registry                # Device registry (retained)
    └── {module}/
        ├── cmd                 # Plugin commands
        └── evt                 # Plugin events
```

### Message Format
All messages follow a standardized envelope format:
```json
{
  "req_id": "uuid",
  "actor": "api|orchestrator|user",
  "ts": "2024-01-01T00:00:00Z",
  "action": "start|stop|configure",
  "params": {}
}
```

## Plugin System

### Device Modules
- Extend `lab_agent.base.Module`
- Handle commands and publish status
- Manage external processes and resources
- Example: NDI viewer control

### Orchestrator Plugins
- Extend `lab_orchestrator.plugin_api.OrchestratorPlugin`
- Provide REST API endpoints
- Offer web UI components
- Handle scheduling and resource locking
- Example: NDI control panel

## Development Workflow

### Adding New Features

1. **Create module directory**: `features/modules/your_feature/`
2. **Add manifest**: Describe capabilities and configuration
3. **Implement module**: Extend base classes
4. **Create plugin**: Add orchestrator-side functionality
5. **Test integration**: Verify end-to-end functionality

### Local Development

1. **Start infrastructure**: `make start`
2. **Install packages**: `make install-orchestrator install-agent`
3. **Configure agent**: Edit `device-agent/config.yaml`
4. **Run agent**: `lab-agent`
5. **Access UI**: http://localhost:8000

## Next Steps: Git Submodules

To complete the architecture, convert components to separate repositories:

### Recommended Repository Structure

1. **lab-platform** (main/umbrella)
   - Contains: README, Makefile, env.example
   - Submodules: orchestrator, device-agent, features

2. **lab-orchestrator** (infrastructure)
   - Contains: infra/orchestrator/ content
   - Independent versioning and releases

3. **lab-agent** (device communication)
   - Contains: device-agent/ content
   - Independent versioning and releases

4. **lab-features** (pluggable functionality)
   - Contains: features/ content
   - Independent feature development

### Migration Commands

```bash
# Create separate repositories
git subtree push --prefix=infra/orchestrator origin orchestrator-branch
git subtree push --prefix=device-agent origin agent-branch
git subtree push --prefix=features origin features-branch

# Convert to submodules
git submodule add <orchestrator-repo-url> infra/orchestrator
git submodule add <agent-repo-url> device-agent
git submodule add <features-repo-url> features
```

## Benefits of New Architecture

1. **Modularity**: Clear separation of concerns
2. **Reusability**: Features work across different deployments
3. **Scalability**: Independent component development
4. **Maintainability**: Clean interfaces and documentation
5. **Deployability**: Single-command infrastructure setup
6. **Extensibility**: Plugin system for new functionality

The architecture successfully transforms the working MVP into a production-ready, modular platform suitable for laboratory automation and device management.
