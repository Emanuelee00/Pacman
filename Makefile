all: run

UV := $(shell command -v uv 2>/dev/null || printf '%s/.local/bin/uv' "$$HOME")

install:
	@echo "Checking if uv is installed..."
	@if [ ! -x "$(UV)" ]; then \
		echo "uv could not be found. Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	else \
		echo "uv is already installed."; \
	fi

	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		$(UV) venv; \
		echo "Virtual environment created successfully."; \
	else \
		echo "Virtual environment already exists."; \
	fi

	@$(UV) sync --dev
	@$(UV) pip install -e . > /dev/null

run: install
	@if [ -z "$${DISPLAY:-}$${WAYLAND_DISPLAY:-}" ]; then \
		echo "No graphical display found on this server."; \
		echo "Use 'make web-run' and open http://localhost:8020 instead."; \
		exit 1; \
	fi
	@echo "Running game..."
	@$(UV) run python3 pac-man.py config.json

debug:
	@echo "Running game in debug mode..."
	@$(UV) run python3 -m pdb pac-man.py config.json

lint:
	@echo "Running lint checks..."
	@$(UV) run flake8 .
	@$(UV) run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo "Running strict lint checks..."
	@$(UV) run flake8 .
	@$(UV) run mypy . --strict

clean:
	@echo "Cleaning up generated files and caches..."
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	@rm -rf .mypy_cache .venv ./src/pacman.egg-info/ dist build

package: install
	@echo "Building standalone executable..."
	@$(UV) run pyinstaller pacman.spec --noconfirm
	@echo "Done. Executable is in dist/pacman"

# Requires pygbag (uv tool install pygbag), kept out of pyproject.toml since it
# would pull in pygame-ce alongside the desktop build's pygame. See web/README.md.
web-sync:
	@echo "Syncing sources into web/..."
	@./web/build.sh

web-build: web-sync
	@echo "Building the WASM bundle..."
	@$(UV) tool run --from pygbag==0.9.3 pygbag \
		--template web/pygbag.tmpl --build web
	@echo "Done. Files ready in web/build/web/"

web-run: web-sync
	@echo "Serving the WASM build locally..."
	@$(UV) tool run --from pygbag==0.9.3 pygbag \
		--template web/pygbag.tmpl --port 8020 web

re: clean all
