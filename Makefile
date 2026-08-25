all: run

install:
	@echo "Checking if uv is installed..."
	@if ! command -v uv &> /dev/null; then \
		echo "uv could not be found. Installing uv..."; \
		pip install --user uv > /dev/null; \
		echo "uv installed successfully."; \
	else \
		echo "uv is already installed."; \
	fi

	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		uv venv; \
		echo "Virtual environment created successfully."; \
	else \
		echo "Virtual environment already exists."; \
	fi

	@uv sync --dev
	@uv pip install -e . > /dev/null

run: install
	@echo "Running game..."
	@uv run python3 pac-man.py config.json

debug:
	@echo "Running game in debug mode..."
	@uv run python3 -m pdb pac-man.py config.json

lint:
	@echo "Running lint checks..."
	@uv run flake8 .
	@uv run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo "Running strict lint checks..."
	@uv run flake8 .
	@uv run mypy . --strict

clean:
	@echo "Cleaning up generated files and caches..."
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	@rm -rf .mypy_cache .venv ./src/pacman.egg-info/ dist build

package: install
	@echo "Building standalone executable..."
	@uv run pyinstaller pacman.spec --noconfirm
	@echo "Done. Executable is in dist/pacman"

# Requires pygbag (pip install pygbag), kept out of pyproject.toml since it
# would pull in pygame-ce alongside the desktop build's pygame. See web/README.md.
web-build:
	@echo "Syncing sources into web/ and building the WASM bundle..."
	@./web/build.sh
	@python3 -m pygbag --build web
	@echo "Done. Files ready in web/build/web/"

web-run:
	@echo "Syncing sources into web/ and serving the WASM build locally..."
	@./web/build.sh
	@python3 -m pygbag web

re: clean all
