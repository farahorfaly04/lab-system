# MQTT Protocol Reference

Complete reference for MQTT communication patterns, topics, and message formats used in the Lab Platform.

## Overview

The Lab Platform uses MQTT as the primary communication protocol between the orchestrator and device agents. This document defines the topic structure, message formats, and communication patterns.

## Broker Configuration

### EMQX Settings
- **Version**: EMQX 5.8+
- **Protocol**: MQTT 3.1.1/5.0
- **Port**: 1883 (plain), 8883 (TLS)
- **Authentication**: Username/password
- **QoS**: Primarily QoS 1 for guaranteed delivery

### Connection Parameters
```bash
# Standard configuration
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USERNAME=mqtt
MQTT_PASSWORD=secure_password
MQTT_KEEPALIVE=60
MQTT_CLEAN_SESSION=true
```

## Topic Hierarchy

### Complete Topic Structure
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

### Topic Examples
```bash
# Device metadata
/lab/device/ndi-device-01/meta

# Device status
/lab/device/ndi-device-01/status

# Module command
/lab/device/ndi-device-01/ndi/cmd

# Module status
/lab/device/ndi-device-01/ndi/status

# Plugin event
/lab/orchestrator/ndi/evt

# Registry snapshot
/lab/orchestrator/registry
```

## Message Formats

### Standard Message Envelope
All messages use a standardized JSON envelope:

```json
{
  "req_id": "550e8400-e29b-41d4-a716-446655440000",
  "actor": "api|orchestrator|user|system",
  "ts": "2024-01-01T12:00:00Z",
  "action": "start|stop|configure|status",
  "params": {
    "key": "value"
  }
}
```

### Field Descriptions
- **req_id**: Unique request identifier (UUID v4)
- **actor**: Who initiated the request
- **ts**: ISO 8601 timestamp in UTC
- **action**: Command or event type
- **params**: Action-specific parameters

## Device Communication

### Device Registration
When a device agent starts, it publishes metadata:

**Topic**: `/lab/device/{device_id}/meta`
**QoS**: 1 (retained)
**Payload**:
```json
{
  "req_id": "meta-550e8400-e29b-41d4-a716-446655440000",
  "actor": "system",
  "ts": "2024-01-01T12:00:00Z",
  "device_id": "ndi-device-01",
  "labels": ["ndi", "production", "classroom-a"],
  "modules": ["ndi"],
  "ip_address": "192.168.1.100",
  "platform": "linux",
  "python_version": "3.11.5",
  "agent_version": "1.0.0"
}
```

### Device Status
Periodic status updates:

**Topic**: `/lab/device/{device_id}/status`
**QoS**: 1 (retained)
**Payload**:
```json
{
  "req_id": "status-550e8400-e29b-41d4-a716-446655440000",
  "actor": "system",
  "ts": "2024-01-01T12:00:00Z",
  "device_id": "ndi-device-01",
  "status": "online",
  "uptime": 3600,
  "cpu_percent": 15.5,
  "memory_percent": 45.2,
  "disk_percent": 60.1,
  "network_tx_bytes": 1024000,
  "network_rx_bytes": 2048000
}
```

### Device Commands
Commands sent to devices:

**Topic**: `/lab/device/{device_id}/cmd`
**QoS**: 1
**Payload**:
```json
{
  "req_id": "cmd-550e8400-e29b-41d4-a716-446655440000",
  "actor": "api",
  "ts": "2024-01-01T12:00:00Z",
  "action": "restart",
  "params": {
    "graceful": true,
    "timeout": 30
  }
}
```

### Device Events
Events from devices:

**Topic**: `/lab/device/{device_id}/evt`
**QoS**: 1
**Payload**:
```json
{
  "req_id": "cmd-550e8400-e29b-41d4-a716-446655440000",
  "actor": "system",
  "ts": "2024-01-01T12:00:01Z",
  "success": true,
  "error": null,
  "data": {
    "action": "restart",
    "duration_ms": 1500,
    "status": "restarted"
  }
}
```

## Module Communication

### Module Commands
Commands sent to specific modules:

**Topic**: `/lab/device/{device_id}/{module}/cmd`
**QoS**: 1
**Payload**:
```json
{
  "req_id": "mod-550e8400-e29b-41d4-a716-446655440000",
  "actor": "api",
  "ts": "2024-01-01T12:00:00Z",
  "action": "start",
  "params": {
    "source": "Camera 1 (192.168.1.50)",
    "quality": "high",
    "record": false
  }
}
```

### Module Configuration
Configuration updates for modules:

**Topic**: `/lab/device/{device_id}/{module}/cfg`
**QoS**: 1 (retained)
**Payload**:
```json
{
  "req_id": "cfg-550e8400-e29b-41d4-a716-446655440000",
  "actor": "orchestrator",
  "ts": "2024-01-01T12:00:00Z",
  "config": {
    "ndi_path": "/usr/local/lib/ndi",
    "log_level": "INFO",
    "auto_start": false,
    "default_source": "Camera 1"
  }
}
```

### Module Status
Status updates from modules:

**Topic**: `/lab/device/{device_id}/{module}/status`
**QoS**: 1 (retained)
**Payload**:
```json
{
  "req_id": "status-550e8400-e29b-41d4-a716-446655440000",
  "actor": "system",
  "ts": "2024-01-01T12:00:00Z",
  "device_id": "ndi-device-01",
  "module": "ndi",
  "status": "running",
  "current_source": "Camera 1 (192.168.1.50)",
  "processes": {
    "viewer": {"pid": 1234, "status": "running"},
    "recorder": {"pid": null, "status": "stopped"}
  },
  "stats": {
    "frames_received": 1500,
    "frames_dropped": 2,
    "bitrate_mbps": 25.6
  }
}
```

### Module Events
Events from modules:

**Topic**: `/lab/device/{device_id}/{module}/evt`
**QoS**: 1
**Payload**:
```json
{
  "req_id": "mod-550e8400-e29b-41d4-a716-446655440000",
  "actor": "system",
  "ts": "2024-01-01T12:00:01Z",
  "success": true,
  "error": null,
  "data": {
    "action": "start",
    "source": "Camera 1 (192.168.1.50)",
    "pid": 1234,
    "duration_ms": 850
  }
}
```

## Orchestrator Communication

### Registry Updates
Device registry snapshots:

**Topic**: `/lab/orchestrator/registry`
**QoS**: 1 (retained)
**Payload**:
```json
{
  "req_id": "registry-550e8400-e29b-41d4-a716-446655440000",
  "actor": "orchestrator",
  "ts": "2024-01-01T12:00:00Z",
  "devices": {
    "ndi-device-01": {
      "device_id": "ndi-device-01",
      "labels": ["ndi", "production"],
      "status": "online",
      "last_seen": "2024-01-01T11:59:55Z",
      "modules": ["ndi"],
      "ip_address": "192.168.1.100"
    }
  },
  "modules": ["ndi", "projector"],
  "plugin_count": 2,
  "device_count": 1
}
```

### Plugin Commands
Commands from plugins to orchestrator:

**Topic**: `/lab/orchestrator/{module}/cmd`
**QoS**: 1
**Payload**:
```json
{
  "req_id": "plugin-550e8400-e29b-41d4-a716-446655440000",
  "actor": "user",
  "ts": "2024-01-01T12:00:00Z",
  "action": "reserve",
  "params": {
    "device_id": "ndi-device-01",
    "lease_s": 300,
    "reason": "maintenance"
  }
}
```

### Plugin Events
Events from plugins:

**Topic**: `/lab/orchestrator/{module}/evt`
**QoS**: 1
**Payload**:
```json
{
  "req_id": "plugin-550e8400-e29b-41d4-a716-446655440000",
  "actor": "orchestrator",
  "ts": "2024-01-01T12:00:01Z",
  "success": true,
  "error": null,
  "data": {
    "action": "reserve",
    "device_id": "ndi-device-01",
    "lease_expires": "2024-01-01T12:05:00Z"
  }
}
```

## QoS and Retention Policies

### Quality of Service Levels
- **QoS 0**: Fire and forget (not used)
- **QoS 1**: At least once delivery (standard)
- **QoS 2**: Exactly once delivery (not used)

### Retention Policies
- **Retained Messages**: Status and metadata topics
- **Non-Retained**: Commands and events
- **TTL**: No explicit TTL, rely on broker configuration

### Topic Patterns
| Topic Pattern | QoS | Retained | Purpose |
|---------------|-----|----------|---------|
| `/lab/device/+/meta` | 1 | Yes | Device metadata |
| `/lab/device/+/status` | 1 | Yes | Device status |
| `/lab/device/+/cmd` | 1 | No | Device commands |
| `/lab/device/+/evt` | 1 | No | Device events |
| `/lab/device/+/+/cmd` | 1 | No | Module commands |
| `/lab/device/+/+/cfg` | 1 | Yes | Module configuration |
| `/lab/device/+/+/status` | 1 | Yes | Module status |
| `/lab/device/+/+/evt` | 1 | No | Module events |
| `/lab/orchestrator/registry` | 1 | Yes | Registry snapshot |
| `/lab/orchestrator/+/cmd` | 1 | No | Plugin commands |
| `/lab/orchestrator/+/evt` | 1 | No | Plugin events |

## Error Handling

### Error Message Format
```json
{
  "req_id": "original-request-id",
  "actor": "system",
  "ts": "2024-01-01T12:00:01Z",
  "success": false,
  "error": "Device not found",
  "error_code": "DEVICE_NOT_FOUND",
  "data": null
}
```

### Common Error Codes
- **DEVICE_NOT_FOUND**: Device not in registry
- **MODULE_NOT_AVAILABLE**: Module not loaded
- **INVALID_PARAMS**: Invalid command parameters
- **TIMEOUT**: Command execution timeout
- **PERMISSION_DENIED**: Access denied
- **RESOURCE_BUSY**: Device or resource in use
- **NETWORK_ERROR**: Communication failure

### Timeout Handling
- **Command Timeout**: 30 seconds default
- **Response Timeout**: 60 seconds for status requests
- **Keepalive**: 60 seconds for MQTT connections
- **Retry Policy**: Exponential backoff, max 3 retries

## Message Validation

### Required Fields
All messages must include:
- `req_id`: Valid UUID v4
- `actor`: Non-empty string
- `ts`: Valid ISO 8601 timestamp
- `action`: Valid action name (for commands)

### Field Validation
- **req_id**: UUID v4 format
- **actor**: Max 50 characters, alphanumeric + underscore
- **ts**: ISO 8601 with timezone (preferably UTC)
- **action**: Max 50 characters, alphanumeric + underscore + hyphen
- **params**: Valid JSON object, max 64KB

### Schema Validation
```python
# Example validation schema (JSON Schema)
{
  "type": "object",
  "required": ["req_id", "actor", "ts"],
  "properties": {
    "req_id": {
      "type": "string",
      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    },
    "actor": {
      "type": "string",
      "maxLength": 50,
      "pattern": "^[a-zA-Z0-9_]+$"
    },
    "ts": {
      "type": "string",
      "format": "date-time"
    },
    "action": {
      "type": "string",
      "maxLength": 50,
      "pattern": "^[a-zA-Z0-9_-]+$"
    },
    "params": {
      "type": "object"
    }
  }
}
```

## Security Considerations

### Authentication
- **Username/Password**: MQTT broker authentication
- **Client Certificates**: For production deployments
- **Access Control Lists**: Topic-based permissions

### Authorization
```bash
# Example EMQX ACL rules
# Allow devices to publish to their own topics
allow {username} publish /lab/device/{username}/#

# Allow orchestrator to publish/subscribe to all topics
allow orchestrator pubsub /lab/#

# Deny all other access
deny all
```

### Message Encryption
- **TLS**: MQTT over TLS (port 8883)
- **Payload Encryption**: Optional application-level encryption
- **Certificate Validation**: Verify broker certificates

## Monitoring and Debugging

### MQTT Tools
```bash
# Subscribe to all topics
mosquitto_sub -h localhost -p 1883 -u mqtt -P password -t '/lab/+/+' -v

# Publish test message
mosquitto_pub -h localhost -p 1883 -u mqtt -P password -t '/lab/test' -m '{"test": true}'

# Monitor specific device
mosquitto_sub -h localhost -p 1883 -u mqtt -P password -t '/lab/device/ndi-01/+' -v

# Monitor all events
mosquitto_sub -h localhost -p 1883 -u mqtt -P password -t '/lab/+/+/evt' -v
```

### EMQX Monitoring
```bash
# Connection statistics
curl http://localhost:18083/api/v5/stats

# Client list
curl http://localhost:18083/api/v5/clients

# Topic metrics
curl http://localhost:18083/api/v5/topics

# Message statistics
curl http://localhost:18083/api/v5/messages/statistics
```

### Message Tracing
```python
# Python MQTT client with logging
import paho.mqtt.client as mqtt
import logging

logging.basicConfig(level=logging.DEBUG)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("/lab/+/+")

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}")
    print(f"Payload: {msg.payload.decode()}")
    print("---")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("mqtt", "password")
client.connect("localhost", 1883, 60)
client.loop_forever()
```

## Performance Optimization

### Message Size
- **Recommended**: < 1KB per message
- **Maximum**: 64KB per message
- **Large Payloads**: Use message splitting or external storage

### Connection Pooling
- **Device Agents**: Single persistent connection
- **Orchestrator**: Connection per plugin (optional)
- **Clients**: Reuse connections when possible

### Topic Design
- **Avoid Wildcards**: In production subscriptions
- **Use Specific Topics**: For targeted messages
- **Minimize Retained**: Only for essential state

### Batch Operations
```json
{
  "req_id": "batch-550e8400-e29b-41d4-a716-446655440000",
  "actor": "api",
  "ts": "2024-01-01T12:00:00Z",
  "action": "batch",
  "params": {
    "commands": [
      {
        "device_id": "ndi-01",
        "action": "start",
        "params": {"source": "Camera 1"}
      },
      {
        "device_id": "ndi-02", 
        "action": "start",
        "params": {"source": "Camera 2"}
      }
    ]
  }
}
```

This MQTT protocol reference provides the complete specification for message formats and communication patterns in the Lab Platform.
