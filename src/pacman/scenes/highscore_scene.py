"""Scene for displaying high scores."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from pygame import Color
from pacman.settings import WHITE, YELLOW
from pacman.parser import load_highscores
from .scene import Scene

if TYPE_CHECKING:
    from pacman.game import Game
    from pacman.parser import HighscoreEntry


class HighScoreScene(Scene):
    """Class representing the high score scene."""

    def __init__(self, game: Game) -> None:
        """
        Initialize the high score scene.

        Args:
            game: Reference to the main Game object.
        """
        super().__init__(game)
        self.top_10: list[HighscoreEntry] = []

    def _top_10(self) -> None:
        """Load and sort the top 10 high scores."""
        highscores = load_highscores()
        self.top_10 = sorted(
            highscores.scores, key=lambda s: s.score, reverse=True)[:10]

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle events for the high score scene.

        Args:
            events: List of Pygame events to process.
        """
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_BACKSPACE:
                    self.exit_scene()

    def enter_scene(self) -> None:
        """Push the high score scene onto the game's scene stack."""
        self._top_10()
        super().enter_scene()

    def update(self) -> None:
        """Update the high score scene."""
        ...

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the high score scene.

        Args:
            surface: The Pygame surface to render the scene on.
        """
        font = self.game.fonts["medium"]
        sw = surface.get_width()
        sh = surface.get_height()
        surface.fill((0, 0, 0))
        title = font.render("HIGH SCORES", True, Color(WHITE))
        surface.blit(title, (sw // 2 - title.get_width() // 2, sh // 8))
        for i, entry in enumerate(self.top_10):
            text = font.render(
                f"{i + 1}. {entry.name}  {entry.score}", True, Color(YELLOW)
                )
            surface.blit(
                text,
                (
                    sw // 2 - text.get_width() // 2,
                    sh // 8 + (sh // 8) + i * (sh // 15)
                )
            )
