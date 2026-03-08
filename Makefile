.PHONY: help install test test-unit test-integration test-all lint format clean build docker docker-test docker-run

# Default target
help:
	@echo "Netpulse - Network Monitoring Tool"
	@echo "================================"
	@echo ""
	@echo "Available targets:"
	@echo "  install      Install the application and dependencies"
	@echo "  test         Run all tests"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-integration Run integration tests (requires Docker)"
	@echo "  test-all     Run unit and integration tests"
	@echo "  lint         Run code linting"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean build artifacts and cache"
	@echo "  build        Build DEB package"
	@echo "  docker       Build Docker image"
	@echo "  docker-test  Run tests in Docker"
	@echo "  docker-run   Run application in Docker"
	@echo "  dev          Start development server"
	@echo ""

# Installation
install:
	pip install -r requirements.txt
	pip install -e .
	sudo apt-get install -y librespeed-cli iputils-ping || echo "Please install librespeed-cli manually"

# Testing
test:
	pytest tests/ -v --cov=netpulse --cov-report=term-missing

test-unit:
	NETPULSE_TEST_MODE=true pytest tests/test_config_simple.py tests/test_database.py tests/test_speedtest.py tests/test_config.py tests/test_web.py::TestWebInterface::test_api_health_endpoint tests/test_web.py::TestWebInterface::test_api_data_endpoint tests/test_web.py::TestWebInterface::test_api_stats_endpoint -v --cov=netpulse --cov-report=term-missing -m "not integration"

test-integration:
	@echo "Starting application for integration tests..."
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f docker-compose.test.yml --profile integration up --build --abort-on-container-exit; \
	elif command -v docker >/dev/null 2>&1; then \
		docker compose -f docker-compose.test.yml --profile integration up --build --abort-on-container-exit; \
	else \
		echo "Docker not found. Please install Docker."; \
		echo "Integration tests require Docker to run."; \
	fi

test-all: test-unit test-integration

# Code quality
lint:
	@echo "Running flake8..."
	flake8 netpulse/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 netpulse/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "Running bandit security scan..."
	bandit -r netpulse/
	@echo "Running safety check..."
	safety check

format:
	@echo "Formatting code with black..."
	black netpulse/
	@echo "Sorting imports with isort..."
	isort netpulse/

format-check:
	@echo "Checking code formatting..."
	black --check netpulse/
	isort --check-only netpulse/

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f *.deb
	rm -f test-results.xml
	rm -f integration-results.xml
	docker-compose down --volumes --remove-orphans || true
	docker system prune -f

# Building
build:
	@echo "Building DEB package..."
	chmod +x build.sh
	./build.sh

# Docker
docker:
	@echo "Building Docker image..."
	docker build -t netpulse:latest .

docker-test:
	@echo "Running tests in Docker..."
	docker-compose -f docker-compose.test.yml --profile test up --build --abort-on-container-exit

docker-run:
	@echo "Running Netpulse in Docker..."
	docker-compose up --build

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down

# Development
dev:
	@echo "Starting development server..."
	python -m netpulse.web

# Database operations
db-init:
	@echo "Initializing database..."
	python -c "from netpulse.database import db; print('Database initialized')"

db-cleanup:
	@echo "Cleaning old database entries..."
	python -c "from netpulse.database import db; print(f'Cleaned {db.cleanup_old_data(30)} old entries')"

# Manual testing
test-bandwidth:
	@echo "Running bandwidth test..."
	netpulse-measure --type bandwidth --verbose

test-latency:
	@echo "Running latency test..."
	netpulse-measure --type latency --verbose

# Development helpers
watch:
	@echo "Watching for changes and running tests..."
	watchmedo shell-command --patterns="*.py" --recursive --command='make test-unit' .

install-dev:
	pip install -r requirements.txt
	pip install -e .
	pip install black isort flake8 bandit safety pytest-cov pytest-mock watchdog
	sudo apt-get install -y librespeed-cli iputils-ping || echo "Please install librespeed-cli manually"

# Quick start for development
quickstart: install-dev
	@echo "Netpulse development environment ready!"
	@echo "Run 'make dev' to start the development server"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make lint' to check code quality"
