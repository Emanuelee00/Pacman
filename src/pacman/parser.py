"""Module for parsing game configuration and highscores in the Pacman game."""

from __future__ import annotations

import json
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    ConfigDict
)
from typing import Any, Literal
from pathlib import Path
from random import randint

DEFAULT_LEVELS = [
    {
        "id": 1,
        "width": 9,
        "height": 9,
        "ghosts": [
            {"type": "Blinky", "strategy": "euclidean"},
            {"type": "Pinky", "strategy": "euclidean"},
            {"type": "Inky", "strategy": "euclidean"},
            {"type": "Clyde", "strategy": "euclidean"},
        ],
    },
    {
        "id": 2,
        "width": 11,
        "height": 10,
        "ghosts": [
            {"type": "Blinky", "strategy": "bfs"},
            {"type": "Pinky", "strategy": "euclidean"},
            {"type": "Inky", "strategy": "bfs"},
            {"type": "Clyde", "strategy": "euclidean"},
        ],
    },
    {
        "id": 3,
        "width": 12,
        "height": 11,
        "ghosts": [
            {"type": "Blinky", "strategy": "euclidean"},
            {"type": "Pinky", "strategy": "bfs"},
            {"type": "Inky", "strategy": "euclidean"},
            {"type": "Clyde", "strategy": "bfs"},
        ],
    },
    {
        "id": 4,
        "width": 13,
        "height": 12,
        "ghosts": [
            {"type": "Blinky", "strategy": "bfs"},
            {"type": "Pinky", "strategy": "bfs"},
            {"type": "Inky", "strategy": "euclidean"},
            {"type": "Clyde", "strategy": "euclidean"},
        ],
    },
    {
        "id": 5,
        "width": 14,
        "height": 13,
        "ghosts": [
            {"type": "Blinky", "strategy": "euclidean"},
            {"type": "Pinky", "strategy": "euclidean"},
            {"type": "Inky", "strategy": "bfs"},
            {"type": "Clyde", "strategy": "bfs"},
        ],
    },
    {
        "id": 6,
        "width": 15,
        "height": 14,
        "ghosts": [
            {"type": "Blinky", "strategy": "bfs"},
            {"type": "Pinky", "strategy": "bfs"},
            {"type": "Inky", "strategy": "bfs"},
            {"type": "Clyde", "strategy": "bfs"},
        ],
    },
    {
        "id": 7,
        "width": 15,
        "height": 13,
        "ghosts": [
            {"type": "Blinky", "strategy": "euclidean"},
            {"type": "Pinky", "strategy": "bfs"},
            {"type": "Inky", "strategy": "euclidean"},
            {"type": "Clyde", "strategy": "bfs"},
        ],
    },
    {
        "id": 8,
        "width": 15,
        "height": 12,
        "ghosts": [
            {"type": "Blinky", "strategy": "bfs"},
            {"type": "Pinky", "strategy": "bfs"},
            {"type": "Inky", "strategy": "euclidean"},
            {"type": "Clyde", "strategy": "euclidean"},
        ],
    },
    {
        "id": 9,
        "width": 16,
        "height": 13,
        "ghosts": [
            {"type": "Blinky", "strategy": "euclidean"},
            {"type": "Pinky", "strategy": "euclidean"},
            {"type": "Inky", "strategy": "bfs"},
            {"type": "Clyde", "strategy": "bfs"},
        ],
     },
    {
        "id": 10,
        "width": 17,
        "height": 14,
        "ghosts": [
            {"type": "Blinky", "strategy": "bfs"},
            {"type": "Pinky", "strategy": "euclidean"},
            {"type": "Inky", "strategy": "bfs"},
            {"type": "Clyde", "strategy": "euclidean"},
        ],
     },
]


def _build_default_levels() -> list[LevelConfig]:
    """Build the default level configuration list."""
    return [LevelConfig.model_validate(level) for level in DEFAULT_LEVELS]


class GhostConfig(BaseModel):
    """Configuration for a single ghost inside a level."""

    model_config = ConfigDict(extra="ignore")

    type: Literal["Blinky", "Pinky", "Inky", "Clyde"]
    strategy: Literal["euclidean", "bfs"]


class LevelConfig(BaseModel):
    """Configuration for a single game level."""

    model_config = ConfigDict(extra="ignore")

    id: int = Field(ge=1)
    width: int = Field(ge=5, le=18)
    height: int = Field(ge=5, le=18)
    ghosts: list[GhostConfig] = Field(default_factory=list)


class GameConfig(BaseModel):
    """Global game configuration, loaded from config.json."""

    model_config = ConfigDict(extra="ignore")

    highscore_filename: str = Field(default="highscores.json", min_length=1)
    lives: int = Field(default=3, ge=0)
    points_per_pacgum: int = Field(default=10, gt=0)
    points_per_super_pacgum: int = Field(default=50, gt=0)
    points_per_ghost: int = Field(default=200, gt=0)
    seed: int = Field(default=42)
    level_max_time: int = Field(default=120, gt=0)
    levels: list[LevelConfig] = Field(default_factory=_build_default_levels)

    @field_validator("levels", mode="before")
    @classmethod
    def validate_levels(cls, levels: Any) -> list[LevelConfig]:
        """
        Validate the levels configuration.

        Args:
            levels: The raw levels data from the config file.
        Returns:
            A list of validated LevelConfig instances.
        """
        if not levels:
            print(
                "Warning: No levels defined in config. Adding default levels."
                )
            return _build_default_levels()
        validated_levels: list[LevelConfig] = []

        for level_data in levels:
            try:
                validated_levels.append(LevelConfig.model_validate(level_data))
            except ValidationError as e:
                print(
                    f"Error: Invalid level configuration. "
                    f"Using random default level. "
                    f"Details: {e}"
                    )
                validated_levels.append(LevelConfig.model_validate(
                    DEFAULT_LEVELS[randint(0, len(DEFAULT_LEVELS) - 1)]
                    ))
        return validated_levels


class HighscoreEntry(BaseModel):
    """A single entry in the leaderboard: player name and score."""

    name: str = Field(min_length=1, max_length=20)
    score: int = Field(ge=0)


class Highscores(BaseModel):
    """Full leaderboard loaded from highscores.json."""

    scores: list[HighscoreEntry] = []


def get_highscore_path() -> Path:
    """
    Get the path to the highscores.json file.

    Returns:
        Path object pointing to the highscores.json file
        in the user's local data directory.
    """
    data_dir = Path.home() / ".local" / "share" / "pacman_game"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "highscores.json"


def load_config(path: str | Path = "config.json") -> GameConfig:
    """Load and validate the game configuration from a JSON file.

    Args:
        path: Path to the JSON config file.

    Returns:
        A validated GameConfig instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValidationError: If the JSON data fails validation.
    """
    path = Path(path)

    if path.suffix != ".json":
        print("Error: File must be in JSON format. Using default config.")
        return GameConfig()

    if path.is_dir():
        print("Error: You can't insert a directory. Using default config.")
        return GameConfig()

    try:
        clear_data = []
        with open(path) as f:
            for line in f:
                if not line.lstrip().startswith(("#", "//")):
                    clear_data.append(line)
            data = json.loads("".join(clear_data))
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Failed to load config file. Using default config.")
        return GameConfig()

    try:
        return GameConfig.model_validate(data)
        # return filter_config(game_config)
    except ValidationError as e:
        print(
            f"Error: Config validation failed. Using default config. "
            f"Details: {e}"
            )
        return GameConfig()


def load_highscores() -> Highscores:
    """
    Load the leaderboard from a JSON file.

    Returns:
        A Highscores instance containing the loaded leaderboard data.
    """
    resolved_path = get_highscore_path()

    if not resolved_path.exists():
        highscores = Highscores()
        save_highscores(highscores)
        return highscores

    with open(resolved_path) as f:
        data = json.load(f)

    return Highscores.model_validate(data)


def save_highscores(highscores: Highscores) -> None:
    """Save the leaderboard to a JSON file.

    Args:
        highscores: The Highscores object to save.
    """
    path = get_highscore_path()

    with open(path, "w") as f:
        json.dump(highscores.model_dump(), f, indent=2)
