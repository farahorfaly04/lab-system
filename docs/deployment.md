# Deployment Guide

This guide covers deploying the Lab Platform in various environments, from development to production.

## Prerequisites

### System Requirements

**Infrastructure (Orchestrator)**:
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, Windows with WSL2
- **CPU**: 2+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum
- **Network**: Stable internet connection, ports 1883, 8000, 18083 available

**Edge Devices (Device Agents)**:
- **OS**: Linux (Raspberry Pi OS, Ubuntu), macOS, Windows
- **CPU**: 1+ core (ARM or x86)
- **RAM**: 1GB minimum, 2GB recommended
- **Storage**: 8GB minimum
- **Network**: Stable connection to MQTT broker

### Software Dependencies

- **Docker**: 20.10+ with Docker Compose
- **Python**: 3.8+ (for development and direct installation)
- **Git**: For repository management

## Development Deployment

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd lab_platform

# Configure environment
cp env.example .env
# Edit .env with your settings

# Start infrastructure
make start

# Verify deployment
make check-readiness
make health-check
```

### Manual Setup

#### 1. Infrastructure Setup

```bash
cd infra

# Configure environment
cp env.example .env

# Edit configuration
cat > .env << EOF
# MQTT Configuration
MQTT_USERNAME=mqtt
MQTT_PASSWORD=your-secure-password
EMQX_DASHBOARD__DEFAULT_PASSWORD=your-admin-password

# Database Configuration
POSTGRES_PASSWORD=your-db-password
DATABASE_URL=postgresql://postgres:your-db-password@db:5432/lab_platform

# Service Ports
ORCHESTRATOR_PORT=8000
EMQX_MQTT_PORT=1883
EMQX_DASHBOARD_PORT=18083

# Security
TZ=UTC
EOF

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f orchestrator
```

#### 2. Device Agent Setup

```bash
cd device-agent

# Install in development mode
pip install -e .

# Configure agent
cp config.yaml.example config.yaml
cp env.example .env

# Edit configuration
cat > .env << EOF
DEVICE_ID=dev-device-01
DEVICE_LABELS=development,lab
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USERNAME=mqtt
MQTT_PASSWORD=your-secure-password
HEARTBEAT_INTERVAL_S=10
FEATURES_PATH=../features
EOF

# Run agent
lab-agent

# Or use make commands
make setup-config
make install
make run
```

#### 3. Verification

```bash
# Check all components
make check-readiness-verbose

# Access services
open http://localhost:8000        # Orchestrator UI
open http://localhost:18083       # EMQX Dashboard

# Test MQTT connectivity
make test-mqtt
```

## Production Deployment

### Infrastructure Deployment

#### Option 1: Docker Compose (Recommended for small deployments)

```bash
# Production environment file
cat > .env << EOF
# MQTT Configuration
MQTT_USERNAME=lab_mqtt_user
MQTT_PASSWORD=$(openssl rand -base64 32)
EMQX_DASHBOARD__DEFAULT_PASSWORD=$(openssl rand -base64 32)

# Database Configuration
POSTGRES_PASSWORD=$(openssl rand -base64 32)
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/lab_platform

# Service Configuration
ORCHESTRATOR_PORT=8000
EMQX_MQTT_PORT=1883
EMQX_DASHBOARD_PORT=18083

# Security
TZ=America/New_York
EOF

# Production compose file
cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  emqx:
    image: emqx/emqx:5.8
    container_name: lab-emqx-prod
    restart: always
    environment:
      EMQX_DASHBOARD__DEFAULT_PASSWORD: \${EMQX_DASHBOARD__DEFAULT_PASSWORD}
      TZ: \${TZ}
    ports:
      - "\${EMQX_MQTT_PORT}:1883"
      - "\${EMQX_DASHBOARD_PORT}:18083"
    networks: [labnet]
    volumes:
      - emqx_data:/opt/emqx/data
      - emqx_log:/opt/emqx/log
      - ./emqx.conf:/opt/emqx/etc/emqx.conf:ro
    healthcheck:
      test: ["CMD", "emqx", "ctl", "status"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    container_name: lab-db-prod
    restart: always
    environment:
      POSTGRES_DB: lab_platform
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
      TZ: \${TZ}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks: [labnet]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  orchestrator:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: lab-orchestrator-prod
    restart: always
    environment:
      MQTT_HOST: emqx
      MQTT_PORT: 1883
      MQTT_USERNAME: \${MQTT_USERNAME}
      MQTT_PASSWORD: \${MQTT_PASSWORD}
      DATABASE_URL: \${DATABASE_URL}
      HOST: 0.0.0.0
      PORT: 8000
      LOG_LEVEL: INFO
      TZ: \${TZ}
    ports:
      - "\${ORCHESTRATOR_PORT}:8000"
    networks: [labnet]
    depends_on:
      emqx:
        condition: service_healthy
      db:
        condition: service_healthy
    volumes:
      - ./features:/app/features:ro
      - orchestrator_logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  labnet:
    driver: bridge

volumes:
  emqx_data:
  emqx_log:
  postgres_data:
  orchestrator_logs:
EOF

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

#### Option 2: Kubernetes

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: lab-platform
---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: lab-platform-config
  namespace: lab-platform
data:
  MQTT_HOST: "lab-emqx"
  MQTT_PORT: "1883"
  LOG_LEVEL: "INFO"
---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: lab-platform-secrets
  namespace: lab-platform
type: Opaque
stringData:
  MQTT_USERNAME: "lab_mqtt_user"
  MQTT_PASSWORD: "your-secure-password"
  POSTGRES_PASSWORD: "your-db-password"
  DATABASE_URL: "postgresql://postgres:your-db-password@lab-postgres:5432/lab_platform"
---
# emqx-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lab-emqx
  namespace: lab-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app: lab-emqx
  template:
    metadata:
      labels:
        app: lab-emqx
    spec:
      containers:
      - name: emqx
        image: emqx/emqx:5.8
        ports:
        - containerPort: 1883
        - containerPort: 18083
        env:
        - name: EMQX_DASHBOARD__DEFAULT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: lab-platform-secrets
              key: MQTT_PASSWORD
        volumeMounts:
        - name: emqx-data
          mountPath: /opt/emqx/data
        livenessProbe:
          exec:
            command: ["emqx", "ctl", "status"]
          initialDelaySeconds: 30
          periodSeconds: 30
      volumes:
      - name: emqx-data
        persistentVolumeClaim:
          claimName: emqx-pvc
---
# Apply with: kubectl apply -f k8s/
```

### Device Agent Production Setup

#### Systemd Service (Linux)

```bash
# Install agent
cd device-agent
pip install -e .

# Create service file
sudo tee /etc/systemd/system/lab-agent.service << EOF
[Unit]
Description=Lab Platform Device Agent
After=network.target
Wants=network.target

[Service]
Type=simple
User=lab-agent
Group=lab-agent
WorkingDirectory=/opt/lab-platform/device-agent
EnvironmentFile=/opt/lab-platform/device-agent/.env
ExecStart=/usr/local/bin/lab-agent
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/lab-platform/device-agent/logs

[Install]
WantedBy=multi-user.target
EOF

# Create user and directories
sudo useradd -r -s /bin/false lab-agent
sudo mkdir -p /opt/lab-platform/device-agent/{logs,config}
sudo chown -R lab-agent:lab-agent /opt/lab-platform/device-agent

# Configure environment
sudo tee /opt/lab-platform/device-agent/.env << EOF
DEVICE_ID=$(hostname)
DEVICE_LABELS=production,lab
MQTT_HOST=your-mqtt-broker.example.com
MQTT_PORT=1883
MQTT_USERNAME=lab_mqtt_user
MQTT_PASSWORD=your-secure-password
HEARTBEAT_INTERVAL_S=30
FEATURES_PATH=/opt/lab-platform/features
LOG_LEVEL=INFO
EOF

# Enable and start service
sudo systemctl enable lab-agent
sudo systemctl start lab-agent
sudo systemctl status lab-agent
```

#### Docker Container (Alternative)

```dockerfile
# Dockerfile.agent
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -r -s /bin/false lab-agent

# Install agent
WORKDIR /app
COPY device-agent/ .
RUN pip install -e .

# Copy configuration
COPY features/ /app/features/

# Switch to non-root user
USER lab-agent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

CMD ["lab-agent"]
```

```bash
# Build and run
docker build -f Dockerfile.agent -t lab-platform/agent .

docker run -d \
  --name lab-agent-prod \
  --restart always \
  --env-file device-agent/.env \
  -v /opt/lab-platform/features:/app/features:ro \
  lab-platform/agent
```

## SSL/TLS Configuration

### MQTT over TLS

```bash
# Generate certificates
mkdir -p certs
cd certs

# Create CA
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -days 365 -key ca-key.pem -out ca-cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=Lab Platform CA"

# Create server certificate
openssl genrsa -out server-key.pem 4096
openssl req -new -key server-key.pem -out server.csr \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=mqtt.example.com"
openssl x509 -req -in server.csr -CA ca-cert.pem -CAkey ca-key.pem \
  -CAcreateserial -out server-cert.pem -days 365

# Configure EMQX
cat > emqx.conf << EOF
listeners.ssl.default {
  bind = "0.0.0.0:8883"
  ssl_options {
    keyfile = "/opt/emqx/etc/certs/server-key.pem"
    certfile = "/opt/emqx/etc/certs/server-cert.pem"
    cacertfile = "/opt/emqx/etc/certs/ca-cert.pem"
    verify = verify_peer
    fail_if_no_peer_cert = true
  }
}
EOF
```

### HTTPS for Orchestrator

```nginx
# nginx.conf
upstream orchestrator {
    server localhost:8000;
}

server {
    listen 443 ssl http2;
    server_name lab.example.com;

    ssl_certificate /etc/ssl/certs/lab.example.com.crt;
    ssl_certificate_key /etc/ssl/private/lab.example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    location / {
        proxy_pass http://orchestrator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://orchestrator;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Monitoring and Logging

### Prometheus Monitoring

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'lab-orchestrator'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'emqx'
    static_configs:
      - targets: ['localhost:18083']
    metrics_path: '/api/v5/prometheus/stats'
```

### Log Aggregation

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  kibana:
    image: kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200

  filebeat:
    image: elastic/filebeat:8.8.0
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro

volumes:
  elasticsearch_data:
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups/lab-platform"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec lab-db-prod pg_dump -U postgres lab_platform | \
  gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# Backup EMQX configuration
docker exec lab-emqx-prod tar czf - /opt/emqx/data | \
  cat > $BACKUP_DIR/emqx_data_$DATE.tar.gz

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Disaster Recovery

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
BACKUP_DIR="/opt/backups/lab-platform"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

# Stop services
docker-compose down

# Restore database
zcat $BACKUP_DIR/$BACKUP_FILE | \
  docker exec -i lab-db-prod psql -U postgres lab_platform

# Restart services
docker-compose up -d

echo "Restore completed from: $BACKUP_FILE"
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs orchestrator
docker-compose logs emqx
docker-compose logs db

# Check ports
netstat -tlnp | grep -E ':(1883|8000|18083)'

# Check disk space
df -h

# Check memory
free -h
```

#### Device Agent Connection Issues
```bash
# Test MQTT connectivity
mosquitto_pub -h your-broker -p 1883 -u mqtt -P password -t test -m "hello"

# Check agent logs
journalctl -u lab-agent -f

# Test DNS resolution
nslookup your-broker

# Check firewall
sudo ufw status
```

#### Performance Issues
```bash
# Monitor resources
docker stats

# Check database performance
docker exec lab-db-prod psql -U postgres -c "
  SELECT query, calls, total_time, mean_time 
  FROM pg_stat_statements 
  ORDER BY total_time DESC LIMIT 10;"

# Monitor MQTT
curl -u admin:password http://localhost:18083/api/v5/stats
```

### Health Checks

```bash
# Automated health monitoring
#!/bin/bash
# health-check.sh

SERVICES=("orchestrator:8000/health" "emqx:18083" "postgres:5432")
FAILED=0

for service in "${SERVICES[@]}"; do
  IFS=':' read -r name endpoint <<< "$service"
  
  if ! curl -f -s "http://localhost:$endpoint" > /dev/null; then
    echo "❌ $name is unhealthy"
    FAILED=1
  else
    echo "✅ $name is healthy"
  fi
done

exit $FAILED
```

## Security Hardening

### Network Security
```bash
# Firewall rules
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 1883/tcp    # MQTT
sudo ufw allow 8883/tcp    # MQTT TLS
sudo ufw enable
```

### Container Security
```dockerfile
# Security-hardened Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r lab && useradd -r -g lab lab

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set security options
USER lab
WORKDIR /app

# Health check with timeout
HEALTHCHECK --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

This deployment guide covers the essential aspects of deploying the Lab Platform in various environments. For specific deployment scenarios or advanced configurations, refer to the individual component documentation.
