"""pygbag entry point for the Pacman web (WASM) build.

Prepends vendor/ to sys.path so `import pydantic` resolves to the WASM-safe
shim (real pydantic-core has no Emscripten build) and `import mazegenerator`
resolves to the vendored pure-Python copy of the wheel, before pacman itself
is imported.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "vendor"))

from pacman.game import Game  # noqa: E402
from pacman.parser import load_config  # noqa: E402


async def main() -> None:
    """Load config.json and run the game."""
    config = load_config("config.json")
    game = Game(config)
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
