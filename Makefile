# Makefile for haomnilogic-local
# Provides a simple interface for building and running the Docker container

# Configuration
IMAGE_NAME = haomnilogic-local
TAG = latest

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install dependencies locally using uv (requires uv installed locally)
	@echo "Installing dependencies locally..."
	@uv sync --all-extras

.PHONY: build
build: ## Build the Docker image
	@echo "Building Docker image $(IMAGE_NAME):$(TAG)..."
	@docker build -t $(IMAGE_NAME):$(TAG) .

.PHONY: sync-lock
sync-lock: build ## Re-generate uv.lock inside Docker and sync it back to the host
	@echo "Syncing uv.lock from container to host..."
	@docker create --name temp_lock_sync $(IMAGE_NAME):$(TAG)
	@docker cp temp_lock_sync:/app/uv.lock ./uv.lock
	@docker rm temp_lock_sync
	@echo "uv.lock updated successfully."

.PHONY: run
run: ## Run the omnilogic CLI from inside the container (use ARGS="--help" for options)
	@docker run --rm -it $(IMAGE_NAME):$(TAG) $(ARGS)

.PHONY: debug
debug: ## Run the container with a bash shell for debugging
	@docker run --rm -it --entrypoint /bin/bash $(IMAGE_NAME):$(TAG)

.PHONY: clean
clean: ## Remove the docker image
	@docker rmi $(IMAGE_NAME):$(TAG) 2>/dev/null || true
