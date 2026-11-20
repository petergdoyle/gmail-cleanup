# gmail-cleanup — developer Makefile (utility-gui)
# Dev convenience over a uv-first fallback chain. Not required at runtime.
.DEFAULT_GOAL := help
.PHONY: help setup install uninstall web ui dev-up dev-down dev-status test lint lint-fix clean

UV := uv

help: ## Show this help
	@echo "gmail-cleanup — make targets"
	@echo "  setup        Create .venv + install dev deps"
	@echo "  test         Run the test suite (pytest)"
	@echo "  lint         Run ruff"
	@echo "  lint-fix     Run ruff --fix"
	@echo "  clean        Remove transient dev artifacts"
	@echo "  install      Install the command for your user (uv tool)"
	@echo "  web          Build the React UI into the package"
	@echo "  ui           Build-if-needed + serve the web UI (127.0.0.1)"
	@echo "  dev-up       Start the local web UI and open a browser"
	@echo "  dev-down     Stop the managed local web UI"
	@echo "  dev-status   Check the managed local web UI"

setup: ## Create venv + editable install with dev deps
	@command -v $(UV) > /dev/null 2>&1 || { echo "uv required: https://docs.astral.sh/uv/"; exit 1; }
	@$(UV) sync --extra dev
	@echo "Done. Try: uv run gmail --help"

install: web ## Build the UI and install the command for the current user
	@$(UV) tool install --force --reinstall --no-cache .

uninstall: ## Remove the installed command
	@$(UV) tool uninstall gmail-cleanup 2>/dev/null || echo "gmail-cleanup was not installed."

web: ## Build the React UI into the package (src/*/ui/web)
	@command -v npm > /dev/null 2>&1 || { echo "npm required to build the UI"; exit 1; }
	@cd web-src && npm install && npm run build
	@echo "UI built. Serve it with: make ui (or: uv run gmail ui)"

ui: ## Build-if-needed and serve the web UI (127.0.0.1; Ctrl-C to stop)
	@$(UV) run gmail ui

dev-up: web ## Build, start the local development UI, and open a browser
	@$(UV) run python -m gmail_cleanup.ui.dev up

dev-down: ## Stop only the managed development UI
	@$(UV) run python -m gmail_cleanup.ui.dev down

dev-status: ## Check the managed development UI
	@$(UV) run python -m gmail_cleanup.ui.dev status

test: ## Run tests
	@if [ -x .venv/bin/python ]; then .venv/bin/python -m pytest -q; \
	elif command -v $(UV) > /dev/null 2>&1; then $(UV) run pytest -q; \
	else python3 -m pytest -q; fi

lint: ## Run ruff
	@if command -v $(UV) > /dev/null 2>&1; then $(UV) run ruff check src tests; else ruff check src tests; fi

lint-fix: ## Run ruff --fix
	@if command -v $(UV) > /dev/null 2>&1; then $(UV) run ruff check --fix src tests; else ruff check --fix src tests; fi

clean: ## Remove transient dev artifacts
	@rm -rf .pytest_cache .ruff_cache dist build
	@echo "Clean."
