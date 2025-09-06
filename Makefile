# Lab Platform Makefile

.PHONY: help start stop restart logs status clean install-orchestrator install-agent

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

start: ## Start the infrastructure services
	cd infra && docker-compose up -d

stop: ## Stop the infrastructure services
	cd infra && docker-compose down

restart: ## Restart the infrastructure services
	cd infra && docker-compose restart

logs: ## Show logs from all services
	cd infra && docker-compose logs -f

status: ## Show status of all services
	cd infra && docker-compose ps

clean: ## Clean up containers and volumes
	cd infra && docker-compose down -v --remove-orphans

install-orchestrator: ## Install orchestrator for development
	cd infra/orchestrator && pip install -e .

install-agent: ## Install device agent for development
	cd device-agent && pip install -e .

build: ## Build the orchestrator Docker image
	cd infra && docker-compose build orchestrator

dev-setup: ## Set up development environment
	cp env.example .env
	cd device-agent && cp config.yaml.example config.yaml
	@echo "Edit .env and device-agent/config.yaml with your settings"

test-mqtt: ## Test MQTT connection
	@echo "Testing MQTT connection..."
	@docker run --rm -it --network infra_labnet eclipse-mosquitto:latest \
		mosquitto_sub -h lab-emqx -t '/lab/+/+' -v

health-check: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:8000/api/registry > /dev/null && echo "✓ Orchestrator healthy" || echo "✗ Orchestrator unhealthy"
	@curl -s http://localhost:18083 > /dev/null && echo "✓ EMQX healthy" || echo "✗ EMQX unhealthy"

check-readiness: ## Check readiness of all components
	@echo "Checking Lab Platform readiness..."
	@echo "==================================="
	@echo "Device Agent:"
	@cd device-agent && make check-readiness || true
	@echo ""
	@echo "Orchestrator:"
	@cd infra/orchestrator && make check-readiness || true
	@echo ""
	@echo "NDI Plugin:"
	@cd features/plugins/ndi && python3 check_readiness.py || true
	@echo ""
	@echo "Projector Plugin:"
	@cd features/plugins/projector && python3 check_readiness.py || true
	@echo ""
	@echo "NDI Module:"
	@cd features/modules/ndi && python3 check_readiness.py || true
	@echo ""
	@echo "Projector Module:"
	@cd features/modules/projector && python3 check_readiness.py || true

check-readiness-json: ## Check readiness with JSON output
	@echo '{"components": {'
	@echo -n '"device_agent": '; cd device-agent && python3 scripts/check_readiness.py --json 2>/dev/null || echo '{"overall_status": "ERROR"}'
	@echo ','
	@echo -n '"orchestrator": '; cd infra/orchestrator && python3 scripts/check_readiness.py --json 2>/dev/null || echo '{"overall_status": "ERROR"}'
	@echo ','
	@echo -n '"ndi_plugin": '; cd features/plugins/ndi && python3 check_readiness.py --json 2>/dev/null || echo '{"overall_status": "ERROR"}'
	@echo ','
	@echo -n '"projector_plugin": '; cd features/plugins/projector && python3 check_readiness.py --json 2>/dev/null || echo '{"overall_status": "ERROR"}'
	@echo ','
	@echo -n '"ndi_module": '; cd features/modules/ndi && python3 check_readiness.py --json 2>/dev/null || echo '{"overall_status": "ERROR"}'
	@echo ','
	@echo -n '"projector_module": '; cd features/modules/projector && python3 check_readiness.py --json 2>/dev/null || echo '{"overall_status": "ERROR"}'
	@echo '}}'
