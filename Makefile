ifneq (,$(wildcard dotenv/dev.env))
    include dotenv/dev.env
    export
endif

COMPOSE_FILES := docker-compose.yaml
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: run
run: ## Run
	docker compose up

.PHONY: volume
volume:	## Remove volumes unusing
	docker volume prune

.PHONY: restart
restart:	## restart one/all containers
	docker compose restart $(s)

.PHONY: stop
stop:	## Stop one/all containers
	docker compose stop

.PHONY: logs
logs: ## View logs from one/all containers
	docker compose logs -f $(s)

.PHONY: down
down: ## Stop the services, remove containers and networks
	docker compose down

.PHONY: prune
prune: ## destroy one/all images and volume unusing
	docker system prune

.PHONY: pre-commit
pre-commit: ## Run pre-commit
	pre-commit run --all-files

.PHONY: tests
tests:	## Run tests
	poetry run coverage run -m pytest -v tests

.PHONY: coverage
coverage:	## Glet coverage
	poetry run coverage report -m
