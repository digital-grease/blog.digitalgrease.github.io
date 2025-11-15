.PHONY: help install serve build deploy clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

serve: ## Run local development server
	mkdocs serve

build: ## Build the static site
	mkdocs build

deploy: ## Deploy to GitHub Pages
	mkdocs gh-deploy --force --clean --verbose

clean: ## Clean build artifacts
	rm -rf site/
	rm -rf .cache/

test: serve ## Alias for serve
