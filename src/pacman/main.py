"""Main entry point for the Pacman game."""

import sys
from pacman.game import Game
from pacman.parser import load_config, GameConfig


def main() -> None:
    """Parse and run the game."""
    if len(sys.argv) != 2:
        print("For custom configuration: python main.py <config_file.json>")
        print("Using default configuration")
        config = GameConfig()
    else:
        config = load_config(sys.argv[1])
    game = Game(config)

    game.run()


if __name__ == "__main__":
    main()
