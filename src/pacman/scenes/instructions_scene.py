"""Scene displaying the game instructions."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from pygame import Color
from pacman.settings import WHITE, YELLOW
from .scene import Scene

if TYPE_CHECKING:
    from pacman.game import Game


class InstructionScene(Scene):
    """Class representing the instructions scene."""

    def __init__(self, game: Game) -> None:
        """Initialize the instructions scene."""
        super().__init__(game)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle events for the instructions scene."""
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_BACKSPACE:
                    self.exit_scene()

    def enter_scene(self) -> None:
        """Push the instructions scene onto the game's scene stack."""
        super().enter_scene()

    def update(self) -> None:
        """Update the instructions scene."""
        ...

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the instructions scene.

        Args:
            surface: The Pygame surface to render the scene on.
        """
        font = self.game.fonts["small"]
        font2 = self.game.fonts["large"]
        sw = surface.get_width()
        sh = surface.get_height()
        surface.fill((0, 0, 0))

        title = font.render("INSTRUCTIONS", True, Color(WHITE))
        surface.blit(
            title, (sw // 2 - title.get_width() // 2, sh // 4)
            )
        text = font2.render("DEBROUILLE-TOI", True, Color(YELLOW))
        surface.blit(text, (sw // 2 - text.get_width() // 2, sh // 4 + 60))
        text = font.render(
            "BUT WRITE \"TORETTO\" FOR MORE",
            True,
            Color(YELLOW)
            )
        surface.blit(
            text, (sw // 2 - text.get_width() // 2, sh - sh // 4 - 120)
            )
        text = font.render("Use \"space\" to shoot", True, Color(YELLOW))
        surface.blit(
            text, (sw // 2 - text.get_width() // 2, sh - sh // 4 - 60)
            )
        text = font.render("Press \"Esc\" to exit", True, Color(YELLOW))
        surface.blit(
            text, (sw // 2 - text.get_width() // 2, sh - sh // 4)
            )
