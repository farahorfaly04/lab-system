# Development Guide

Complete guide for developing and extending the Lab Platform, including setup, workflows, and best practices.

## 🚀 Development Environment Setup

### Prerequisites
- **Python 3.8+** with pip and venv
- **Docker and Docker Compose** for infrastructure
- **Git** for version control
- **Node.js 16+** (optional, for UI development)
- **Your favorite IDE** (VS Code, PyCharm, etc.)

### Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd lab_platform

# Set up main environment
cp env.example .env
# Edit .env with your development settings

# Start infrastructure services
make start

# Set up device agent
cd device-agent
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
make setup-config
# Edit .env and config.yaml

# Set up orchestrator
cd ../infra/orchestrator
pip install -e .

# Verify setup
cd ../..
make check-readiness

# Auto-fix any missing dependencies
make check-readiness --fix  # For individual components
```

### Automatic Dependency Installation

The Lab Platform includes intelligent dependency management with automatic installation capabilities:

#### Using Readiness Checks with Auto-Fix

```bash
# Check and automatically install missing dependencies
cd features/modules/ndi
make check-readiness-fix

# Or for individual tools
make install-yuri  # Install yuri_simple for NDI streaming
```

#### Manual Installation

If automatic installation fails, you can install dependencies manually:

```bash
# NDI Module dependencies
cd features/modules/ndi
make install-yuri-apt    # Ubuntu/Debian
make install-yuri-brew   # macOS
make install-yuri-source # From source
```

### IDE Configuration

#### VS Code Settings
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./device-agent/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/venv": true,
    "**/.git": true
  }
}
```

#### PyCharm Configuration
1. Open project in PyCharm
2. Configure Python interpreter: `device-agent/venv/bin/python`
3. Enable code formatting: Black
4. Enable linting: pylint, mypy
5. Set up run configurations for components

## 🏗️ Project Structure

### Repository Layout
```
lab_platform/
├── device-agent/           # Edge device communication
│   ├── src/lab_agent/     # Python package
│   ├── scripts/           # Utility scripts
│   ├── tests/            # Unit tests
│   └── pyproject.toml    # Package configuration
├── infra/                 # Infrastructure services
│   ├── orchestrator/     # Central service
│   │   ├── src/lab_orchestrator/
│   │   ├── alembic/      # Database migrations
│   │   └── tests/
│   └── docker-compose.yaml
├── features/             # Pluggable functionality
│   ├── modules/         # Device-side modules
│   └── plugins/         # Orchestrator-side plugins
├── shared/              # Shared utilities
├── docs/               # Documentation
└── tests/             # Integration tests
```

### Code Organization
- **Packages**: Each component is a proper Python package
- **Configuration**: Environment-based with validation
- **Logging**: Structured logging with JSON output
- **Testing**: Unit tests with pytest, integration tests
- **Documentation**: Inline docstrings + external docs

## 🔧 Development Workflow

### Daily Development
```bash
# Start your development session
make start                    # Start infrastructure
cd device-agent && make run  # Start device agent
cd infra/orchestrator && make run-dev  # Start orchestrator

# Make your changes
# ... edit code ...

# Test your changes
make test                     # Run all tests
make check-readiness         # Verify system health
curl http://localhost:8000/health  # Test API

# Commit your changes
git add .
git commit -m "feat: add new feature"
git push
```

### Testing Workflow
```bash
# Unit tests
cd device-agent && python -m pytest tests/
cd infra/orchestrator && python -m pytest tests/

# Integration tests
cd tests && python -m pytest integration/

# Manual testing
curl http://localhost:8000/api/registry
mosquitto_sub -h localhost -t '/lab/+/+' -v

# Load testing (optional)
cd tests && python load_test.py
```

### Feature Development Workflow
```bash
# Create new feature branch
git checkout -b feature/my-new-feature

# Create module and plugin
mkdir -p features/modules/my_feature
mkdir -p features/plugins/my_feature

# Implement module
cd features/modules/my_feature
# Create manifest.yaml, my_feature.py, check_readiness.py

# Implement plugin
cd ../../../features/plugins/my_feature
# Create manifest.yaml, my_feature.py, check_readiness.py

# Test feature
make check-readiness
# Manual testing...

# Commit and create PR
git add .
git commit -m "feat: add my_feature module and plugin"
git push -u origin feature/my-new-feature
# Create pull request
```

## 🧪 Testing

### Unit Testing

#### Device Agent Tests
```python
# tests/test_agent.py
import pytest
from lab_agent.agent import DeviceAgent
from lab_agent.base import Module

class TestModule(Module):
    name = "test"
    
    def handle_cmd(self, action, params):
        if action == "test":
            return True, None, {"result": "ok"}
        return False, "unknown action", {}

def test_agent_initialization():
    config = {"device_id": "test-device"}
    agent = DeviceAgent(config)
    assert agent.device_id == "test-device"

def test_module_loading():
    # Test module loading logic
    pass

def test_command_handling():
    module = TestModule("test-device", {})
    success, error, data = module.handle_cmd("test", {})
    assert success is True
    assert error is None
    assert data["result"] == "ok"
```

#### Orchestrator Tests
```python
# tests/test_orchestrator.py
import pytest
from fastapi.testclient import TestClient
from lab_orchestrator.host import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_registry_endpoint():
    response = client.get("/api/registry")
    assert response.status_code == 200
    assert "devices" in response.json()

def test_plugin_loading():
    # Test plugin discovery and loading
    pass
```

#### Module Tests
```python
# features/modules/ndi/tests/test_ndi_module.py
import pytest
from ndi_module import NDIModule

def test_ndi_module_init():
    module = NDIModule("test-device", {"ndi_path": "/test/path"})
    assert module.device_id == "test-device"
    assert module.cfg["ndi_path"] == "/test/path"

def test_start_command():
    module = NDIModule("test-device")
    # Mock external dependencies
    success, error, data = module.handle_cmd("start", {"source": "test"})
    # Assert expected behavior
```

### Integration Testing
```python
# tests/integration/test_full_system.py
import pytest
import requests
import paho.mqtt.client as mqtt
import time

class TestSystemIntegration:
    def setup_method(self):
        # Start test infrastructure
        pass
    
    def test_device_registration(self):
        # Start device agent
        # Verify device appears in registry
        response = requests.get("http://localhost:8000/api/registry")
        assert "test-device" in response.json()["devices"]
    
    def test_command_flow(self):
        # Send command via API
        response = requests.post("http://localhost:8000/api/ndi/start", json={
            "device_id": "test-device",
            "params": {"source": "test"}
        })
        assert response.status_code == 200
        
        # Verify MQTT message sent
        # Verify device response
    
    def test_mqtt_communication(self):
        # Test MQTT message flow
        pass
```

### Performance Testing
```python
# tests/performance/load_test.py
import asyncio
import aiohttp
import time

async def test_api_performance():
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        # Send 100 concurrent requests
        tasks = []
        for i in range(100):
            task = session.get("http://localhost:8000/api/registry")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"100 requests completed in {duration:.2f} seconds")
        print(f"Average: {duration/100*1000:.2f} ms per request")
        
        # Assert performance requirements
        assert duration < 10.0  # Should complete within 10 seconds
```

## 🔍 Debugging

### Debug Mode Setup
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Start services with debug
cd device-agent && LOG_LEVEL=DEBUG make run
cd infra/orchestrator && LOG_LEVEL=DEBUG make run-dev
```

### MQTT Debugging
```bash
# Monitor all MQTT traffic
mosquitto_sub -h localhost -p 1883 -u mqtt -P password -t '/lab/+/+' -v

# Test MQTT connectivity
mosquitto_pub -h localhost -p 1883 -u mqtt -P password -t '/lab/test' -m 'hello'

# Check MQTT broker status
curl http://localhost:18083/api/v5/stats
```

### Python Debugging
```python
# Add to your code for debugging
import pdb; pdb.set_trace()  # Python debugger

# Or use logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message with data: %s", data)

# Or use print debugging (temporary)
print(f"DEBUG: variable = {variable}")
```

### Remote Debugging (VS Code)
```python
# Install debugpy
pip install debugpy

# Add to your code
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()  # Optional: wait for debugger
```

VS Code launch configuration:
```json
{
  "name": "Python: Remote Attach",
  "type": "python",
  "request": "attach",
  "connect": {
    "host": "localhost",
    "port": 5678
  }
}
```

## 🎨 Code Style and Standards

### Python Style
```bash
# Install development tools
pip install black pylint mypy isort

# Format code
black .

# Sort imports
isort .

# Lint code
pylint src/

# Type checking
mypy src/
```

### Pre-commit Hooks
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pycqa/pylint
    rev: v2.17.0
    hooks:
      - id: pylint
```

Install pre-commit:
```bash
pip install pre-commit
pre-commit install
```

### Code Review Checklist
- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have type hints
- [ ] Docstrings for public functions/classes
- [ ] Unit tests for new functionality
- [ ] No hardcoded secrets or credentials
- [ ] Error handling is appropriate
- [ ] Logging is structured and meaningful
- [ ] Configuration is externalized
- [ ] Dependencies are properly declared

## 📚 Documentation

### Code Documentation
```python
def handle_command(action: str, params: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """Handle a command and return the result.
    
    Args:
        action: The action to perform (e.g., 'start', 'stop')
        params: Parameters for the action
        
    Returns:
        A tuple of (success, error_message, response_data)
        
    Raises:
        ValueError: If action is invalid
        ConnectionError: If unable to communicate with hardware
        
    Example:
        >>> success, error, data = handle_command('start', {'source': 'Camera 1'})
        >>> if success:
        ...     print(f"Started with PID: {data['pid']}")
    """
    pass
```

### API Documentation
Use FastAPI's automatic documentation:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Lab Platform API",
    description="API for controlling laboratory devices",
    version="1.0.0"
)

class DeviceCommand(BaseModel):
    """Command to send to a device."""
    device_id: str = Field(..., description="Unique device identifier")
    action: str = Field(..., description="Action to perform")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")

@app.post("/api/ndi/start", response_model=CommandResponse)
async def start_ndi(command: DeviceCommand):
    """Start NDI viewer on specified device.
    
    This endpoint sends a start command to the NDI module on the specified device.
    The device must be online and have the NDI module loaded.
    """
    pass
```

### README Updates
When adding features, update relevant README files:
- Main README.md
- Component-specific READMEs
- Feature documentation in features/README.md

## 🚀 Deployment

### Development Deployment
```bash
# Local development
make start
make run

# Docker development
docker-compose -f docker-compose.dev.yml up -d
```

### Production Deployment
```bash
# Build production images
make build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Or use deployment scripts
./scripts/deploy.sh production
```

### CI/CD Pipeline
Example GitHub Actions workflow:
```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd device-agent
          pip install -e .
          pip install pytest
      
      - name: Run tests
        run: |
          cd device-agent
          python -m pytest tests/
      
      - name: Check readiness
        run: |
          make start
          sleep 30
          make check-readiness

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Deployment commands
          echo "Deploying to production..."
```

## 🔧 Advanced Topics

### Custom Module Development
```python
# Advanced module with process management
import subprocess
import signal
from pathlib import Path
from lab_agent.base import Module

class AdvancedModule(Module):
    name = "advanced"
    
    def __init__(self, device_id: str, cfg: dict = None):
        super().__init__(device_id, cfg)
        self.processes = {}
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        self.shutdown()
    
    def start_process(self, name: str, command: str) -> int:
        """Start a managed process."""
        if name in self.processes:
            self.stop_process(name)
        
        proc = subprocess.Popen(
            command.split(),
            preexec_fn=os.setsid,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes[name] = proc
        return proc.pid
    
    def stop_process(self, name: str) -> bool:
        """Stop a managed process."""
        if name not in self.processes:
            return False
        
        proc = self.processes[name]
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        finally:
            del self.processes[name]
        
        return True
    
    def shutdown(self):
        """Clean shutdown of all processes."""
        for name in list(self.processes.keys()):
            self.stop_process(name)
```

### Custom Plugin Development
```python
# Advanced plugin with background tasks
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, BackgroundTasks
from lab_orchestrator.plugin_api import OrchestratorPlugin

class AdvancedPlugin(OrchestratorPlugin):
    module_name = "advanced"
    
    def __init__(self, ctx):
        super().__init__(ctx)
        self.background_tasks = set()
        self.start_background_monitoring()
    
    def start_background_monitoring(self):
        """Start background monitoring task."""
        task = asyncio.create_task(self._monitor_devices())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
    
    async def _monitor_devices(self):
        """Background task to monitor devices."""
        while True:
            try:
                # Monitor device health
                await self._check_device_health()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Back off on error
    
    async def _check_device_health(self):
        """Check health of all devices."""
        for device_id, device_info in self.ctx.registry.devices.items():
            if self.module_name in device_info.get("labels", []):
                # Send health check command
                await self._send_health_check(device_id)
    
    def api_router(self) -> Optional[APIRouter]:
        router = APIRouter()
        
        @router.get("/health")
        async def get_health():
            return {"status": "healthy", "monitored_devices": len(self._get_devices())}
        
        @router.post("/monitor")
        async def start_monitoring(background_tasks: BackgroundTasks):
            background_tasks.add_task(self._monitor_devices)
            return {"status": "monitoring started"}
        
        return router
```

## 🤝 Contributing

### Contribution Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

### Pull Request Guidelines
- Clear description of changes
- Tests for new functionality
- Documentation updates
- Code follows style guidelines
- All CI checks pass

### Issue Reporting
When reporting issues, include:
- System information
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs
- Configuration (sanitized)

## 📞 Getting Help

### Resources
- **Documentation**: Check docs/ directory
- **Examples**: See existing modules and plugins
- **Tests**: Look at test files for usage examples
- **Community**: GitHub discussions and issues

### Development Support
- **Code Review**: Submit PRs for feedback
- **Architecture Questions**: Open GitHub discussions
- **Bug Reports**: Use GitHub issues
- **Feature Requests**: GitHub issues with enhancement label
