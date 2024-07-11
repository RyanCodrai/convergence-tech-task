# MAKEFILE
# Runs main scripts

build: ## build dev image
	docker-compose -f docker-compose.dev.yaml build

build-no-cache: ## build dev image from scratch
	docker-compose -f docker-compose.dev.yaml build --no-cache

deps: ## compile dependencies.
	$(DOCKER_CMD) python3 -m piptools compile --upgrade requirements/prod.in -o requirements.txt
	$(DOCKER_CMD) python3 -m piptools compile --upgrade requirements/dev.in -o requirements.dev.txt

start: ## stops dev services.
	docker-compose -f docker-compose.dev.yaml up -d
	docker exec -it project-assistant-api-dev bash

stop: ## starts dev services.
	docker-compose -f docker-compose.dev.yaml down

restart: stop start ## restart dev services.