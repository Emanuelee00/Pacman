"""Module responsible for managing game levels.

- Loading level configurations.
- Handling level progression.
"""

from __future__ import annotations
from typing import Any
import pygame
from pacman.parser import GameConfig, LevelConfig
from pacman.characters.pacman import Pacman
from pacman.characters import Blinky, Pinky, Inky, Clyde
from pacman.pacgum import PacgumManager
from pacman.strategy import (
    ChaseStrategy,
    BFSChaseStrategy,
    EuclideanChaseStrategy
)
from mazegenerator.mazegenerator import MazeGenerator
from pacman.spritesheet import Spritesheet


class LevelManager():
    """Class representing the level manager."""

    def __init__(
            self,
            config: GameConfig,
            assets: dict[str, Spritesheet]
            ) -> None:
        """
        Initialize the level manager.

        Args:
            config: Game configuration containing level settings.
            assets: Dictionary of loaded game assets.
        """
        self.config = config
        self.levels = config.levels
        self.current_index = 0
        self.assets = assets
        self.load_level()

    @property
    def current_level(self) -> LevelConfig:
        """Return the current level configuration."""
        return self.levels[self.current_index]

    @property
    def is_last(self) -> bool:
        """Check if the current level is the last one."""
        return self.current_index >= len(self.levels) - 1

    def next_level(self) -> bool:
        """Go to the next level if available."""
        if self.is_last:
            return False
        self.current_index += 1
        return True

    def load_level(self) -> None:
        """Load the current level's maze and characters."""
        self._load_maze()
        self._load_characters()
        self.pacman.respawn()
        for ghost in self.ghosts:
            ghost.respawn()

    def _break_wall(self) -> None:
        """Break the walls to create a tunnel in the maze at the middle."""
        # Right wall
        cl = self.current_level
        self.maze[cl.height//2 - 1][cl.width - 1] &= ~8
        self.maze[cl.height//2 - 1][cl.width - 1] |= 4
        self.maze[cl.height//2 - 1][cl.width - 2] &= ~6
        self.maze[cl.height//2][cl.width-1] |= 5
        self.maze[cl.height//2][cl.width-1] &= ~10
        self.maze[cl.height//2 + 1][cl.width-1] &= ~8
        self.maze[cl.height//2 + 1][cl.width-1] |= 1
        self.maze[cl.height//2 + 1][cl.width-2] &= ~3
        self.maze[cl.height//2][cl.width-2] &= ~7

        # Left wall
        self.maze[cl.height//2][0] |= 5
        self.maze[cl.height//2][0] &= ~10
        self.maze[cl.height//2][1] &= ~13
        self.maze[cl.height//2 + 1][0] |= 1
        self.maze[cl.height//2 + 1][0] &= ~2
        self.maze[cl.height//2 + 1][1] &= ~9
        self.maze[cl.height//2 - 1][0] &= ~2
        self.maze[cl.height//2 - 1][0] |= 4
        self.maze[cl.height//2 - 1][1] &= ~12

    def _load_maze(self) -> None:
        """Generate the maze for the current level."""
        self.size = (
            self.current_level.width,
            self.current_level.height
        )
        self.maze = MazeGenerator(size=self.size, seed=self.config.seed).maze
        self._break_wall()

    def _load_characters(self) -> None:
        """Initialize the characters for the current level."""
        def get_strategy(ghost_type: str) -> ChaseStrategy:
            """
            Get the chase strategy for a given ghost type.

            Args:
                ghost_type: The type of ghost (e.g., "Blinky", "Pinky").

            Returns:
                An instance of the appropriate ChaseStrategy subclass.
            """
            ghost_config = next(
                (ghost for ghost in self.current_level.ghosts
                 if ghost.type == ghost_type)
            )
            strategy = ghost_config.strategy if ghost_config else "euclidean"

            if strategy == "bfs":
                return BFSChaseStrategy()
            return EuclideanChaseStrategy()

        self.pacman = Pacman(
            maze=self.maze,
            spritesheet=self.assets["pacman_sprites"],
        )
        self.ghosts: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self.ghosts.add(
            Blinky(
                maze=self.maze,
                pacman=self.pacman,
                spritesheet=self.assets["ghosts_sprites"],
                chase_strategy=get_strategy("Blinky"),
            ),
            Pinky(
                maze=self.maze,
                pacman=self.pacman,
                spritesheet=self.assets["ghosts_sprites"],
                chase_strategy=get_strategy("Pinky"),
            ),
            Clyde(
                maze=self.maze,
                pacman=self.pacman,
                spritesheet=self.assets["ghosts_sprites"],
                chase_strategy=get_strategy("Clyde"),
            )
        )
        self.ghosts.add(
            Inky(
                maze=self.maze,
                pacman=self.pacman,
                blinky=self.ghosts.sprites()[0],
                spritesheet=self.assets["ghosts_sprites"],
                chase_strategy=get_strategy("Inky"),
            )
        )
        self.pacgums: pygame.sprite.Group[Any] = PacgumManager(self.maze).group
        self.missiles: pygame.sprite.Group[Any] = pygame.sprite.Group()
