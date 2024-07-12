# MAKEFILE

# The .PHONY rule is used to declare that 'test' and 'tests' are not files but rather commands.
# This prevents Make from checking for the existence of a file named 'test' or 'tests' and
# ensures that the recipes for these targets are always executed when requested.
.PHONY: test tests build

build: ## Build image
	docker-compose -f docker-compose.dev.yaml build

build-no-cache: ## Build image from scratch
	docker-compose -f docker-compose.dev.yaml build --no-cache

deps: ## Compile dependencies
	python3 -m piptools compile --upgrade requirements/prod.in -o requirements.txt
	python3 -m piptools compile --upgrade requirements/dev.in -o requirements.dev.txt

start: ## Stop containers
	docker-compose -f docker-compose.dev.yaml up -d
	docker exec -it 20-questions bash

stop: ## Start containers
	docker-compose -f docker-compose.dev.yaml down

restart: stop start ## Stop and start containers

app: ## run the application
	python3 src/main.py 

tests:
	coverage run -m pytest && coverage report