# Troubleshooting Guide

Common issues, solutions, and debugging techniques for the Lab Platform.

## 🚨 Quick Diagnostics

### System Health Check
```bash
# Check overall system readiness
make check-readiness-verbose

# Check individual components
cd device-agent && make check-readiness
cd infra/orchestrator && make check-readiness

# Check service health
make health-check
curl http://localhost:8000/health
```

### Service Status
```bash
# Check all services
make status

# View logs
make logs

# Check specific service logs
docker logs lab-orchestrator
docker logs lab-emqx
```

## 🔧 Common Issues

### 1. Services Won't Start

#### Symptoms
- Docker containers fail to start
- Port binding errors
- Connection refused errors

#### Diagnosis
```bash
# Check port availability
netstat -tlnp | grep -E ':(1883|8000|18083|5432)'

# Check Docker status
docker ps -a
docker-compose ps

# Check system resources
df -h          # Disk space
free -h        # Memory
docker system df  # Docker disk usage
```

#### Solutions
```bash
# Free up ports
sudo lsof -ti:8000 | xargs sudo kill -9
sudo lsof -ti:1883 | xargs sudo kill -9

# Clean up Docker resources
docker system prune -f
docker volume prune -f

# Restart Docker daemon
sudo systemctl restart docker

# Check Docker Compose configuration
docker-compose config
```

### 2. Device Agent Connection Issues

#### Symptoms
- Device not appearing in registry
- MQTT connection failures
- "Connection refused" errors

#### Diagnosis
```bash
# Test MQTT broker connectivity
telnet localhost 1883
nc -zv localhost 1883

# Test MQTT authentication
mosquitto_pub -h localhost -p 1883 -u mqtt -P password -t test -m "hello"

# Check device agent logs
tail -f /tmp/lab_agent_*.log
journalctl -u lab-agent -f

# Test DNS resolution
nslookup your-mqtt-broker
dig your-mqtt-broker
```

#### Solutions
```bash
# Check MQTT broker status
docker logs lab-emqx
curl http://localhost:18083  # EMQX dashboard

# Verify credentials in device agent .env
cat device-agent/.env | grep MQTT

# Test with different MQTT client
mosquitto_sub -h localhost -p 1883 -u mqtt -P password -t '/lab/+/+' -v

# Check firewall settings
sudo ufw status
sudo iptables -L

# Restart MQTT broker
docker restart lab-emqx
```

### 3. Module/Plugin Loading Issues

#### Symptoms
- Module not found errors
- Plugin registration failures
- Import errors

#### Diagnosis
```bash
# Check module manifest syntax
python3 -c "import yaml; print(yaml.safe_load(open('manifest.yaml')))"

# Test module import
python3 -c "from my_module import MyModule; print('OK')"

# Check features path
echo $FEATURES_PATH
ls -la $FEATURES_PATH/modules/
ls -la $FEATURES_PATH/plugins/

# Check Python path
python3 -c "import sys; print(sys.path)"
```

#### Solutions
```bash
# Fix manifest syntax errors
yamllint manifest.yaml

# Check Python dependencies
pip install -e .
pip list | grep lab-

# Verify file permissions
chmod +r manifest.yaml
chmod +x *.py

# Check module structure
tree features/modules/my_module/

# Restart services after fixes
make restart
```

### 4. Database Connection Issues

#### Symptoms
- Database connection errors
- Migration failures
- Data persistence issues

#### Diagnosis
```bash
# Test database connectivity
docker exec lab-db psql -U postgres -c "SELECT version();"

# Check database logs
docker logs lab-db

# Verify connection string
echo $DATABASE_URL

# Test connection from orchestrator
docker exec lab-orchestrator python3 -c "
from sqlalchemy import create_engine
engine = create_engine('$DATABASE_URL')
print(engine.execute('SELECT 1').scalar())
"
```

#### Solutions
```bash
# Restart database
docker restart lab-db

# Reset database (⚠️ data loss)
docker-compose down
docker volume rm infra_postgres_data
docker-compose up -d

# Run migrations manually
cd infra/orchestrator
alembic upgrade head

# Check database disk space
docker exec lab-db df -h
```

### 5. Web UI Issues

#### Symptoms
- 404 errors on UI pages
- JavaScript errors
- Template not found errors

#### Diagnosis
```bash
# Check orchestrator logs
docker logs lab-orchestrator

# Test API endpoints
curl http://localhost:8000/api/registry
curl http://localhost:8000/health

# Check template files
ls -la infra/orchestrator/src/lab_orchestrator/ui/templates/

# Browser developer tools
# Check Network tab for failed requests
# Check Console for JavaScript errors
```

#### Solutions
```bash
# Restart orchestrator
docker restart lab-orchestrator

# Clear browser cache
# Ctrl+Shift+R (hard refresh)

# Check plugin registration
curl http://localhost:8000/api/registry

# Verify template files exist
find . -name "*.html" -type f
```

### 6. Performance Issues

#### Symptoms
- Slow response times
- High CPU/memory usage
- Timeout errors

#### Diagnosis
```bash
# Monitor system resources
top -p $(pgrep -f lab)
htop

# Check Docker stats
docker stats

# Monitor network traffic
iftop
nethogs

# Check database performance
docker exec lab-db psql -U postgres -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;"

# Check MQTT metrics
curl -u admin:public http://localhost:18083/api/v5/stats
```

#### Solutions
```bash
# Increase resource limits
# Edit docker-compose.yml:
services:
  orchestrator:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

# Optimize database
docker exec lab-db psql -U postgres -c "VACUUM ANALYZE;"

# Clean up logs
docker exec lab-orchestrator find /app/logs -name "*.log" -mtime +7 -delete

# Monitor and restart if needed
docker restart lab-orchestrator
```

## 🔍 Debug Mode

### Enable Debug Logging

#### Device Agent
```bash
# Environment variable
export LOG_LEVEL=DEBUG
lab-agent

# Configuration file
# Edit config.yaml:
log_level: DEBUG

# Command line
make debug
```

#### Orchestrator
```bash
# Environment variable
export LOG_LEVEL=DEBUG
make run-dev

# Docker environment
docker-compose up -e LOG_LEVEL=DEBUG orchestrator
```

#### View Debug Logs
```bash
# Device agent
tail -f /tmp/lab_agent_*.log

# Orchestrator
docker logs -f lab-orchestrator

# All services
make logs
```

### Verbose Readiness Checks
```bash
# System-wide
make check-readiness-verbose

# Individual components
python3 device-agent/scripts/check_readiness.py --verbose
python3 infra/orchestrator/scripts/check_readiness.py --verbose
python3 features/modules/ndi/check_readiness.py --verbose
```

## 🌐 Network Troubleshooting

### MQTT Communication
```bash
# Test MQTT broker
mosquitto_pub -h localhost -p 1883 -t test -m "hello"
mosquitto_sub -h localhost -p 1883 -t test

# Monitor MQTT traffic
mosquitto_sub -h localhost -p 1883 -t '/lab/+/+' -v

# Test with credentials
mosquitto_pub -h localhost -p 1883 -u mqtt -P password -t test -m "auth_test"

# Check MQTT broker stats
curl http://localhost:18083/api/v5/stats
```

### HTTP/API Testing
```bash
# Test API endpoints
curl -v http://localhost:8000/health
curl -v http://localhost:8000/api/registry

# Test with timeout
curl --max-time 5 http://localhost:8000/api/registry

# Test from different network
curl -v http://your-server-ip:8000/health
```

### Network Connectivity
```bash
# Test connectivity
ping your-server
traceroute your-server
telnet your-server 8000

# Check DNS resolution
nslookup your-server
dig your-server

# Check routing
ip route show
netstat -rn
```

## 🔐 Security Troubleshooting

### Authentication Issues
```bash
# Check MQTT credentials
mosquitto_pub -h localhost -p 1883 -u wrong -P wrong -t test -m "test"

# Verify environment variables
env | grep -E "(MQTT_|DATABASE_)"

# Check credential files
cat device-agent/.env | grep MQTT
```

### Permission Issues
```bash
# Check file permissions
ls -la device-agent/config.yaml
ls -la features/modules/*/

# Check process ownership
ps aux | grep lab

# Fix permissions
chmod 644 config.yaml
chown user:group config.yaml
```

### Network Security
```bash
# Check firewall status
sudo ufw status
sudo iptables -L

# Test port accessibility
nmap -p 1883,8000,18083 localhost

# Check SSL/TLS (if configured)
openssl s_client -connect your-server:8883
```

## 📊 Monitoring and Alerts

### Health Monitoring Script
```bash
#!/bin/bash
# health-monitor.sh

check_service() {
    local service=$1
    local url=$2
    
    if curl -f -s "$url" > /dev/null; then
        echo "✅ $service is healthy"
        return 0
    else
        echo "❌ $service is unhealthy"
        return 1
    fi
}

FAILED=0

check_service "Orchestrator" "http://localhost:8000/health" || FAILED=1
check_service "EMQX" "http://localhost:18083" || FAILED=1

if [ $FAILED -eq 1 ]; then
    echo "⚠️  Some services are unhealthy"
    # Send alert (email, Slack, etc.)
    exit 1
else
    echo "✅ All services are healthy"
    exit 0
fi
```

### Log Analysis
```bash
# Find errors in logs
docker logs lab-orchestrator 2>&1 | grep -i error
grep -i "error\|exception\|failed" /tmp/lab_agent_*.log

# Monitor log patterns
tail -f /var/log/lab-platform.log | grep -E "(ERROR|CRITICAL)"

# Log rotation check
ls -la /var/log/lab-platform/
du -sh /var/log/lab-platform/
```

### Performance Monitoring
```bash
# System metrics
#!/bin/bash
# metrics.sh

echo "=== System Resources ==="
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf "%.2f%%", $3/$2 * 100.0}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{print $5}')"

echo "=== Docker Stats ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo "=== MQTT Stats ==="
curl -s http://localhost:18083/api/v5/stats | jq '.connections.count, .messages.received, .messages.sent'
```

## 🆘 Emergency Procedures

### Complete System Reset
```bash
#!/bin/bash
# emergency-reset.sh

echo "⚠️  EMERGENCY RESET - This will delete all data!"
read -p "Are you sure? (type 'yes'): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted"
    exit 1
fi

echo "Stopping all services..."
make stop

echo "Removing containers and volumes..."
docker-compose down -v --remove-orphans

echo "Cleaning Docker system..."
docker system prune -af

echo "Removing data directories..."
sudo rm -rf data/

echo "Starting fresh..."
make start

echo "✅ System reset complete"
```

### Service Recovery
```bash
#!/bin/bash
# service-recovery.sh

echo "🔄 Starting service recovery..."

# Stop all services
make stop

# Check and fix common issues
echo "Checking disk space..."
df -h

echo "Checking memory..."
free -h

echo "Cleaning up Docker..."
docker system prune -f

echo "Restarting Docker daemon..."
sudo systemctl restart docker

echo "Starting services..."
make start

echo "Waiting for services to be ready..."
sleep 30

echo "Running health checks..."
make check-readiness

echo "✅ Service recovery complete"
```

### Data Backup (Emergency)
```bash
#!/bin/bash
# emergency-backup.sh

BACKUP_DIR="/opt/backups/emergency/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "Creating emergency backup in $BACKUP_DIR..."

# Backup database
docker exec lab-db pg_dump -U postgres lab_platform | gzip > $BACKUP_DIR/database.sql.gz

# Backup configuration
cp -r device-agent/.env $BACKUP_DIR/
cp -r infra/orchestrator/.env $BACKUP_DIR/
cp -r features/ $BACKUP_DIR/

# Backup logs
cp -r /tmp/lab_agent_*.log $BACKUP_DIR/ 2>/dev/null || true

echo "✅ Emergency backup complete: $BACKUP_DIR"
```

## 📞 Getting Help

### Information to Collect
When reporting issues, include:

1. **System Information**:
   ```bash
   uname -a
   docker --version
   docker-compose --version
   python3 --version
   ```

2. **Service Status**:
   ```bash
   make status
   make check-readiness-json
   ```

3. **Logs**:
   ```bash
   make logs > system-logs.txt
   ```

4. **Configuration** (sanitized):
   ```bash
   # Remove passwords before sharing
   cat .env | sed 's/PASSWORD=.*/PASSWORD=***/'
   ```

### Support Channels
- **GitHub Issues**: For bugs and feature requests
- **Documentation**: Check docs/ directory
- **Community Forums**: For general questions
- **Emergency Contact**: For critical production issues

### Self-Help Resources
- **Interactive API Docs**: http://localhost:8000/docs
- **System Metrics**: http://localhost:8000/metrics
- **EMQX Dashboard**: http://localhost:18083
- **Log Files**: Check /tmp/ and Docker logs
- **Configuration Validation**: Use readiness checks
