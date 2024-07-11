# MAKEFILE

build: ## Build image
	docker-compose -f docker-compose.dev.yaml build

build-no-cache: ## Build image from scratch
	docker-compose -f docker-compose.dev.yaml build --no-cache

deps: ## Compile dependencies
	python3 -m piptools compile --upgrade requirements/prod.in -o requirements.txt

start: ## Stop containers
	docker-compose -f docker-compose.dev.yaml up -d
	docker exec -it 20-questions bash

stop: ## Start containers
	docker-compose -f docker-compose.dev.yaml down

restart: ## Stop and sttart containers
	stop start