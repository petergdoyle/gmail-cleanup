# gmail-cleanup — developer Makefile (utility-gui)
# Dev convenience over a uv-first fallback chain. Not required at runtime.
.DEFAULT_GOAL := help
.PHONY: help setup install uninstall web ui up down restart dev-status lab kernel nb-test nb-strip nb-strip-install test lint lint-fix clean

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

setup: ## Create venv + editable install with dev deps
	@command -v $(UV) > /dev/null 2>&1 || { echo "uv required: https://docs.astral.sh/uv/"; exit 1; }
	@$(UV) sync --extra dev
	@echo "Done. Try: uv run gmail --help"

install: ## Install the command for the current user (~/.local/bin via uv tool)
	@$(UV) tool install --force --reinstall --no-cache .

uninstall: ## Remove the installed command
	@$(UV) tool uninstall gmail-cleanup 2>/dev/null || echo "gmail-cleanup was not installed."

web: ## Build the React UI into the package (src/*/ui/web)
	@command -v npm > /dev/null 2>&1 || { echo "npm required to build the UI"; exit 1; }
	@cd web-src && npm install && npm run build
	@echo "UI built. Serve it with: make ui (or: uv run gmail ui)"

ui: ## Build-if-needed and serve the web UI (127.0.0.1; Ctrl-C to stop)
	@$(UV) run gmail ui

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
