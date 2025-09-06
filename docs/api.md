# API Reference

Complete reference for the Lab Platform REST API, including core orchestrator endpoints and plugin-specific APIs.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

Currently, the API uses basic authentication. Future versions will support token-based authentication.

```bash
# Basic usage (no auth required in development)
curl http://localhost:8000/api/registry

# Future token-based auth
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/registry
```

## Core API Endpoints

### Device Registry

#### Get All Devices
```http
GET /api/registry
```

**Response**:
```json
{
  "devices": {
    "ndi-device-01": {
      "device_id": "ndi-device-01",
      "labels": ["ndi", "production"],
      "status": "online",
      "last_seen": "2024-01-01T12:00:00Z",
      "modules": ["ndi"],
      "ip_address": "192.168.1.100"
    }
  },
  "modules": ["ndi", "projector"],
  "ts": "2024-01-01T12:00:00Z"
}
```

#### Remove Device
```http
DELETE /api/registry/devices/{device_id}
```

**Parameters**:
- `device_id` (path): Device identifier

**Response**:
```json
{
  "success": true,
  "message": "Device removed from registry",
  "device_id": "ndi-device-01"
}
```

### Health and Status

#### Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "mqtt": "connected",
    "database": "connected",
    "plugins": 2
  }
}
```

#### Metrics (Prometheus)
```http
GET /metrics
```

**Response**: Prometheus-formatted metrics
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/registry"} 42

# HELP device_count Number of registered devices
# TYPE device_count gauge
device_count 5
```

## Plugin APIs

### NDI Plugin

#### Get NDI Status
```http
GET /api/ndi/status
```

**Response**:
```json
{
  "plugin": "ndi",
  "devices": [
    {
      "device_id": "ndi-device-01",
      "status": "online",
      "labels": ["ndi", "production"]
    }
  ],
  "registry_snapshot": {
    "devices": {...},
    "ts": "2024-01-01T12:00:00Z"
  }
}
```

#### Get NDI Sources
```http
GET /api/ndi/sources
```

**Response**:
```json
{
  "sources": [
    "Camera 1 (192.168.1.50)",
    "Camera 2 (192.168.1.51)",
    "OBS Studio (192.168.1.100)"
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Refresh NDI Sources
```http
GET /api/ndi/sources/refresh
```

**Response**: Same as `/sources` but with forced refresh

#### Get NDI Devices
```http
GET /api/ndi/devices
```

**Response**:
```json
{
  "devices": [
    {
      "device_id": "ndi-device-01",
      "status": "online",
      "labels": ["ndi", "production"]
    }
  ]
}
```

#### Get Specific Device
```http
GET /api/ndi/devices/{device_id}
```

**Response**:
```json
{
  "device": {
    "device_id": "ndi-device-01",
    "labels": ["ndi", "production"],
    "status": "online",
    "last_seen": "2024-01-01T12:00:00Z"
  }
}
```

#### Start NDI Viewer
```http
POST /api/ndi/start
```

**Request Body**:
```json
{
  "device_id": "ndi-device-01",
  "action": "start",
  "params": {
    "source": "Camera 1 (192.168.1.50)",
    "stream": "optional_stream_name",
    "pipeline": "custom_pipeline_command"
  }
}
```

**Response**:
```json
{
  "status": "dispatched",
  "device_id": "ndi-device-01",
  "action": "start"
}
```

#### Stop NDI Viewer
```http
POST /api/ndi/stop
```

**Request Body**:
```json
{
  "device_id": "ndi-device-01",
  "action": "stop",
  "params": {}
}
```

#### Set NDI Input
```http
POST /api/ndi/input
```

**Request Body**:
```json
{
  "device_id": "ndi-device-01",
  "action": "set_input",
  "params": {
    "source": "Camera 2 (192.168.1.51)"
  }
}
```

### Projector Plugin

#### Get Projector Status
```http
GET /api/projector/status
```

**Response**:
```json
{
  "plugin": "projector",
  "devices": [
    {
      "device_id": "projector-01",
      "status": "online",
      "labels": ["projector", "classroom"]
    }
  ]
}
```

#### Get Projector Devices
```http
GET /api/projector/devices
```

#### Control Projector Power
```http
POST /api/projector/power
```

**Request Body**:
```json
{
  "device_id": "projector-01",
  "action": "power",
  "params": {
    "state": "on"  // or "off"
  }
}
```

**Response**:
```json
{
  "status": "dispatched",
  "device_id": "projector-01",
  "action": "power",
  "state": "on"
}
```

#### Set Projector Input
```http
POST /api/projector/input
```

**Request Body**:
```json
{
  "device_id": "projector-01",
  "action": "input",
  "params": {
    "source": "hdmi1"  // or "hdmi2"
  }
}
```

#### Send Projector Command
```http
POST /api/projector/command
```

**Request Body**:
```json
{
  "device_id": "projector-01",
  "action": "command",
  "params": {
    "cmd": "MENU"  // Available: UP, DOWN, LEFT, RIGHT, ENTER, MENU, BACK
  }
}
```

#### Navigate Projector Menu
```http
POST /api/projector/navigate
```

**Request Body**:
```json
{
  "device_id": "projector-01",
  "action": "navigate",
  "params": {
    "direction": "up"  // up, down, left, right, enter, menu, back
  }
}
```

#### Adjust Projector Settings
```http
POST /api/projector/adjust
```

**Request Body**:
```json
{
  "device_id": "projector-01",
  "action": "adjust",
  "params": {
    "type": "h-keystone",  // h-keystone, v-keystone, h-image-shift, v-image-shift
    "value": -5  // Range depends on adjustment type
  }
}
```

## Request/Response Models

### DeviceCommand Model
```json
{
  "device_id": "string (required)",
  "action": "string (required)",
  "params": "object (optional, default: {})"
}
```

### Standard Response Format
```json
{
  "status": "dispatched|success|error",
  "device_id": "string",
  "action": "string",
  "message": "string (optional)",
  "data": "object (optional)"
}
```

### Error Response Format
```json
{
  "detail": "Error message",
  "status_code": 400,
  "type": "validation_error|not_found|internal_error"
}
```

## Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

## Rate Limiting

Currently no rate limiting is implemented. Future versions may include:
- **100 requests/minute** for general API access
- **10 requests/minute** for device control commands
- **1000 requests/minute** for status/read-only endpoints

## WebSocket API (Future)

Real-time updates will be available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Device update:', data);
};

// Subscribe to device updates
ws.send(JSON.stringify({
  type: 'subscribe',
  topics: ['device_status', 'module_events']
}));
```

## SDK and Client Libraries

### Python Client
```python
import requests

class LabPlatformClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_devices(self):
        response = requests.get(f"{self.base_url}/api/registry")
        return response.json()
    
    def start_ndi(self, device_id, source):
        data = {
            "device_id": device_id,
            "action": "start",
            "params": {"source": source}
        }
        response = requests.post(f"{self.base_url}/api/ndi/start", json=data)
        return response.json()

# Usage
client = LabPlatformClient()
devices = client.get_devices()
result = client.start_ndi("ndi-01", "Camera 1")
```

### JavaScript Client
```javascript
class LabPlatformClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async getDevices() {
    const response = await fetch(`${this.baseUrl}/api/registry`);
    return response.json();
  }
  
  async startNDI(deviceId, source) {
    const response = await fetch(`${this.baseUrl}/api/ndi/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_id: deviceId,
        action: 'start',
        params: { source }
      })
    });
    return response.json();
  }
}

// Usage
const client = new LabPlatformClient();
const devices = await client.getDevices();
const result = await client.startNDI('ndi-01', 'Camera 1');
```

## Interactive Documentation

The API includes interactive documentation powered by Swagger UI:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Testing the API

### Using curl
```bash
# Get devices
curl http://localhost:8000/api/registry

# Start NDI with source
curl -X POST http://localhost:8000/api/ndi/start \
  -H "Content-Type: application/json" \
  -d '{"device_id": "ndi-01", "params": {"source": "Camera 1"}}'

# Control projector power
curl -X POST http://localhost:8000/api/projector/power \
  -H "Content-Type: application/json" \
  -d '{"device_id": "proj-01", "params": {"state": "on"}}'
```

### Using Python requests
```python
import requests

# Get devices
response = requests.get('http://localhost:8000/api/registry')
devices = response.json()

# Start NDI
response = requests.post('http://localhost:8000/api/ndi/start', json={
    'device_id': 'ndi-01',
    'params': {'source': 'Camera 1'}
})
result = response.json()
```

### Using Postman
Import the OpenAPI specification from `http://localhost:8000/openapi.json` into Postman for a complete collection of API endpoints.

## Error Handling

### Common Error Scenarios

#### Device Not Found
```json
{
  "detail": "Device not found",
  "status_code": 404
}
```

#### Device Not Supporting Feature
```json
{
  "detail": "Device does not support NDI",
  "status_code": 400
}
```

#### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "device_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "status_code": 422
}
```

#### Device Communication Error
```json
{
  "detail": "Could not communicate with device",
  "status_code": 500
}
```

## Changelog

### Version 1.0.0
- Initial API implementation
- Core device registry endpoints
- NDI and Projector plugin APIs
- Health check and metrics endpoints

### Future Versions
- Authentication and authorization
- WebSocket real-time updates
- Rate limiting
- Bulk operations
- Advanced filtering and pagination
