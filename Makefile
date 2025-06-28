.PHONY: help setup install start dev test clean docker-build docker-up docker-down

help:
	@echo "AVScript AI Chatbot - Available Commands:"
	@echo "  setup          - Run initial setup"
	@echo "  install        - Install dependencies"
	@echo "  start          - Start the application"
	@echo "  dev            - Start in development mode"
	@echo "  test           - Run tests"
	@echo "  preprocess     - Create vector index from PDFs"
	@echo "  health         - Check system health"
	@echo "  clean          - Clean temporary files"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-up      - Start with Docker Compose"
	@echo "  docker-down    - Stop Docker services"

setup:
	@echo "Setting up AVScript AI..."
	chmod +x setup.sh
	./setup.sh

install:
	pip install -r backend/requirements.txt

start:
	python backend/app.py

dev:
	FLASK_ENV=development FLASK_DEBUG=True python backend/app.py

test:
	python -m pytest tests/ -v

preprocess:
	python backend/preprocess.py create

health:
	python backend/health_check.py

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf *.egg-info

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Development helpers
lint:
	flake8 backend/ --max-line-length=100

format:
	black backend/ --line-length=100

requirements:
	pip freeze > backend/requirements.txt

backup-db:
	mongodump --db avscript --out backup/

restore-db:
	mongorestore --db avscript backup/avscript/