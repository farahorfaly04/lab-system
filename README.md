# Lab Platform

A simplified, modular platform for managing laboratory devices and workflows. The platform provides clean separation between infrastructure, device agents, and pluggable features with comprehensive readiness checking.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+ (for development)

### 1. Start Infrastructure
```bash
git clone <repository-url>
cd lab_platform

# Configure environment
cp env.example .env
# Edit .env with your settings

# Start services
make start

# Check readiness and auto-install dependencies
make check-readiness
```

### 2. Access Services
- **Orchestrator Web UI**: http://localhost:8000
- **EMQX Dashboard**: http://localhost:18083 (admin/public)

### 3. Setup Device Agent
```bash
cd device-agent
make install
make setup-config
# Edit .env and config.yaml
make run
```

## 🏗️ Architecture

```
lab_platform/
├── infra/                      # Infrastructure services
│   ├── orchestrator/           # Central coordination service
│   └── docker-compose.yaml    # Full stack (EMQX, DB, Orchestrator)
├── device-agent/               # Edge device communication
├── features/                   # Pluggable functionality
│   ├── modules/               # Device-side modules
│   └── plugins/               # Orchestrator-side plugins
├── shared/                    # Shared utilities
└── docs/                      # Comprehensive documentation
```

## 🔧 Components

### Infrastructure (`infra/`)
- **Orchestrator**: FastAPI service with web UI and REST API
- **EMQX**: MQTT broker for device communication  
- **PostgreSQL**: Database for persistent storage
- **Docker Compose**: Complete stack orchestration

### Device Agent (`device-agent/`)
- **Edge Runtime**: Runs on Raspberry Pi, lab computers, IoT devices
- **Dynamic Module Loading**: Automatically discovers and loads features
- **MQTT Communication**: Connects to orchestrator via MQTT
- **Process Management**: Handles external processes and services

### Features (`features/`)
- **Modules**: Device-side functionality (NDI, Projector, etc.)
- **Plugins**: Orchestrator-side web UI and API extensions
- **Manifest-Driven**: Self-describing with validation

### Shared Utilities (`shared/`)
- **Readiness Checks**: Comprehensive system validation
- **Common Libraries**: Shared code across components

## 📊 Current Features

### NDI (Network Device Interface)
- **Module**: Video streaming control, recording, source switching
- **Plugin**: Web UI for NDI device management, source discovery
- **API**: REST endpoints for programmatic control

### Projector Control  
- **Module**: Serial communication, power/input control, adjustments
- **Plugin**: Web interface for projector management
- **Commands**: Navigation, keystone correction, image shifting

## 🛠️ Development

### Adding New Features

#### 1. Create a Module (Device-side)
```bash
mkdir -p features/modules/my_module
cd features/modules/my_module

# Create manifest.yaml
cat > manifest.yaml << EOF
name: my_module
version: 1.0.0
module_file: my_module.py
class_name: MyModule
actions:
  - name: start
    description: Start the module
EOF

# Implement module
cat > my_module.py << 'EOF'
from lab_agent.base import Module

class MyModule(Module):
    name = "my_module"
    
    def handle_cmd(self, action: str, params: dict) -> tuple[bool, str | None, dict]:
        if action == "start":
            return True, None, {"status": "started"}
        return False, f"Unknown action: {action}", {}
EOF

# Create readiness check
python3 ../../shared/create_module_readiness.py my_module
```

#### 2. Create a Plugin (Orchestrator-side)
```bash
mkdir -p features/plugins/my_plugin
cd features/plugins/my_plugin

# Create manifest.yaml
cat > manifest.yaml << EOF
name: my_plugin
version: 1.0.0
plugin_class: my_plugin:MyPlugin
EOF

# Implement plugin
cat > my_plugin.py << 'EOF'
from lab_orchestrator.plugin_api import OrchestratorPlugin

class MyPlugin(OrchestratorPlugin):
    module_name = "my_module"
    
    def mqtt_topic_filters(self):
        return [f"/lab/orchestrator/{self.module_name}/cmd"]
    
    def handle_mqtt(self, topic: str, payload: dict) -> None:
        # Handle MQTT messages
        pass
EOF

# Create readiness check
python3 ../../shared/create_plugin_readiness.py my_plugin
```

### Testing and Validation

```bash
# Check system readiness
make check-readiness

# Test specific components
cd device-agent && make check-readiness
cd infra/orchestrator && make check-readiness

# Run with verbose output
make check-readiness-verbose

# Get JSON status
make check-readiness-json
```

## 🌐 MQTT Protocol

Structured topic hierarchy for reliable communication:

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
└── orchestrator/
    ├── registry                # Device registry (retained)
    └── {module}/
        ├── cmd                 # Plugin commands
        └── evt                 # Plugin events
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture Guide](docs/architecture.md)** - Detailed system design
- **[Deployment Guide](docs/deployment.md)** - Production deployment
- **[Developer Guide](docs/development.md)** - Development workflows
- **[API Reference](docs/api.md)** - Complete API documentation
- **[MQTT Protocol](docs/mqtt.md)** - Message formats and topics
- **[Feature Development](docs/features.md)** - Creating modules and plugins
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

### Component Documentation

- **[Device Agent](device-agent/README.md)** - Edge device communication
- **[Orchestrator](infra/orchestrator/README.md)** - Central coordination service
- **[Features](features/README.md)** - Pluggable modules and plugins

## ⚡ Key Improvements

### Simplified Architecture
- **Reduced Complexity**: Streamlined codebase with clear separation of concerns
- **Shared Libraries**: Common functionality in reusable components
- **Consistent Patterns**: Unified approach across all components

### Comprehensive Readiness Checks
- **System Validation**: Verify configuration, dependencies, and connectivity
- **Component Health**: Individual and aggregate status reporting
- **Development Aid**: Quick identification of setup issues

### Enhanced Developer Experience
- **Clear Documentation**: Step-by-step guides for all scenarios
- **Template Generation**: Automated scaffolding for new features
- **Consistent APIs**: Uniform interfaces across components

## 🔍 Monitoring

### Health Checks
```bash
# Overall system health
make health-check

# Individual components
curl http://localhost:8000/health
curl http://localhost:18083  # EMQX
```

### Logging
- **Structured Logs**: JSON format with consistent fields
- **Component Isolation**: Separate logs per service
- **Debug Mode**: Detailed logging for troubleshooting

### Metrics
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Request counts, response times
- **MQTT Metrics**: Message throughput, connection counts

## 🚨 Troubleshooting

### Quick Diagnostics
```bash
# Check all components
make check-readiness-verbose

# Check specific issues
cd device-agent && python3 scripts/check_readiness.py --verbose
cd infra/orchestrator && python3 scripts/check_readiness.py --verbose
```

### Common Issues
1. **MQTT Connection Failed**: Check broker status and credentials
2. **Module Not Loading**: Verify manifest.yaml and Python imports
3. **Plugin Registration Failed**: Check orchestrator logs and plugin syntax
4. **Database Connection**: Verify DATABASE_URL and service health

See **[Troubleshooting Guide](docs/troubleshooting.md)** for detailed solutions.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Run readiness checks: `make check-readiness`
5. Submit pull request

## 📄 License

[Your License Here]

## 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)