"""Main game class for managing game state, scenes, and assets."""

from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path
import asyncio
import sys
import pygame
from pacman.scenes.menu_scene import MenuScene
from pacman.spritesheet import Spritesheet
from pacman.settings import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    FPS,
    FONT,
    FONT_IN,
    FONT_OUT,
    FontSize
)
from pacman.parser import load_highscores

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.font import Font
    from pacman.parser import GameConfig, HighscoreEntry, Highscores
    from pacman.scenes.scene import Scene


class Game:
    """
    Class representing the main game application.

    This class is responsible for managing game state, scenes, and assets.
    """

    def __init__(self, config: GameConfig) -> None:
        """Initialize the game.

        Args:
            config: Configuration object containing game settings.

        Attributes:
            current_dir: Path to the current directory.
            fonts: Dictionary of loaded fonts.
            config: Game configuration settings.
            screen: Pygame display surface.
            running: Boolean indicating if the game loop is running.
            clock: Pygame clock for managing frame rate.
            dt: Delta time between frames.
            assets: Dictionary of loaded game assets.
            scenes_stack: Stack of active game scenes.
            score: Current player score.
            highscores: Loaded high scores from storage.
        """
        pygame.init()

        self.current_dir: Path

        if getattr(sys, "frozen", False):
            self.current_dir = Path(getattr(sys, "_MEIPASS")) / "pacman"
        else:
            self.current_dir = Path(__file__).parent

        self.fonts: dict[str, Font] = {
            "title_in": pygame.font.Font(
                self.current_dir / "assets" / FONT_IN, FontSize.XX_LARGE),
            "title_out": pygame.font.Font(
                self.current_dir / "assets" / FONT_OUT, FontSize.XX_LARGE),
            "x_small": pygame.font.Font(
                self.current_dir / "assets" / FONT, FontSize.X_SMALL),
            "small": pygame.font.Font(
                self.current_dir / "assets" / FONT, FontSize.SMALL),
            "medium": pygame.font.Font(
                self.current_dir / "assets" / FONT, FontSize.MEDIUM),
            "large": pygame.font.Font(
                self.current_dir / "assets" / FONT, FontSize.LARGE),
            "x_large": pygame.font.Font(
                self.current_dir / "assets" / FONT, FontSize.X_LARGE),
        }
        self.config: GameConfig = config
        self.screen: Surface = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.dt: float = 0

        self.scenes_stack: list[Scene] = []
        self.assets: dict[str, Spritesheet] = {}
        self._load_assets()
        self._load_cursor()
        self._load_scenes()
        self.score: int = 0
        self.highscores: Highscores = load_highscores()

    @property
    def high_score(self) -> HighscoreEntry | None:
        """Get the highest score from the loaded high scores."""
        if not self.highscores.scores:
            return None
        return max(self.highscores.scores, key=lambda x: x.score)

    def _load_scenes(self) -> None:
        """Initialize and load the main game scenes."""
        self.menu_scene = MenuScene(self)
        self.scenes_stack.append(self.menu_scene)

    def _load_assets(self) -> None:
        """Load game assets such as spritesheets and images."""
        maze_tiles = Spritesheet(
            self.current_dir / "assets" / "maze_tiles.png"
            )
        ghosts_sprites = Spritesheet(
            self.current_dir / "assets" / "ghosts_sprites.png"
            )
        pacman_sprites = Spritesheet(
            self.current_dir / "assets" / "pacman_sprites.png"
            )
        missile_sprites = Spritesheet(
            self.current_dir / "assets" / "missile_sprites.png"
            )

        self.assets = {
            "maze_tiles": maze_tiles,
            "ghosts_sprites": ghosts_sprites,
            "pacman_sprites": pacman_sprites,
            "missile_sprites": missile_sprites,
        }

    def _load_cursor(self) -> None:
        """Load and prepare the cursor image for menu navigation."""
        pacman_sprites = self.assets["pacman_sprites"]
        self.cursor_animation = {
            0: pygame.transform.scale(
                pacman_sprites.get_sprite(0, 54, 48, 48),
                (28, 28)
                ),
            1: pygame.transform.scale(
                pacman_sprites.get_sprite(54, 54, 48, 48),
                (28, 28)
                ),
            2: pygame.transform.scale(
                pacman_sprites.get_sprite(108, 54, 48, 48),
                (28, 28)
                ),
        }

    def draw_text(
            self,
            surface: pygame.Surface,
            text: str,
            color: pygame.Color,
            x: int,
            y: int,
            size: str = "medium"
            ) -> pygame.Rect:
        """Draw and blit text on the given surface."""
        font = self.fonts.get(size, self.fonts["medium"])
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)
        return text_rect

    async def run(self) -> None:
        """Run the main game loop."""
        while self.running:

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((0, 0, 0))
            current_scene = self.scenes_stack[-1]
            current_scene.handle_events(events)
            current_scene.update()
            for scene in self.scenes_stack:
                scene.render(self.screen)

            pygame.display.flip()
            self.dt = self.clock.tick(FPS)
            await asyncio.sleep(0)
        pygame.quit()
