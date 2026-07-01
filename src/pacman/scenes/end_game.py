"""Scene for handling end of game logic, including high score entry."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from pygame import Color
from pacman.settings import WHITE, YELLOW, RED
from pacman.parser import (
    load_highscores,
    save_highscores,
    HighscoreEntry,
)
from .scene import Scene

if TYPE_CHECKING:
    from pacman.game import Game


class EndgameScene(Scene):
    """Class representing the end game scene (Win/Loss)."""

    def __init__(self, game: Game, remaining_lives: int) -> None:
        """
        Initialize the end game scene.

        Args:
            game: Reference to the main Game object.
            remaining_lives: Number of lives remaining for the player.
        """
        self.game = game
        self._score = game.score
        self._remaining_lives = remaining_lives
        self._player_name = ""
        self._err_msg = ""
        game.score = 0

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle events for the end game scene.

        Args:
            events: List of Pygame events to process.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if len(self._player_name) < 3:
                        self._err_msg = "Name must be at least 3 characters"
                    else:
                        hs = load_highscores()
                        hs.scores.append(
                            HighscoreEntry(
                                name=self._player_name,
                                score=self._score)
                                )
                        save_highscores(hs)
                        self.game.highscores = hs
                        self.exit_scene()
                        from .menu_scene import MenuScene
                        MenuScene(self.game).enter_scene()

                elif event.key == pygame.K_BACKSPACE:
                    self._player_name = self._player_name[:-1]
                    self._err_msg = ""
                elif event.unicode.isprintable():
                    if len(self._player_name) < 11:
                        self._player_name += event.unicode
                        self._err_msg = ""
                    else:
                        self._err_msg = "Name must not exceed 10 characters"

    def update(self) -> None:
        """Update the end game scene."""
        ...

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the end game scene.

        Args:
            surface: The Pygame surface to render the scene on.
        """
        font = self.game.fonts["medium"]
        mid_w = surface.get_width() // 2
        mid_h = surface.get_height() // 2
        surface.fill((0, 0, 0))

        prompt = font.render("INSERT NAME:", True, Color(WHITE))
        name = font.render(self._player_name + "_", True, Color(YELLOW))
        surface.blit(
            prompt,
            (mid_w - prompt.get_width() // 2, mid_h)
            )
        surface.blit(
            name,
            (mid_w - name.get_width() // 2, mid_h + mid_h // 5)
            )

        score = font.render(f"SCORE: {self._score}", True, Color(WHITE))
        surface.blit(
            score,
            (mid_w - score.get_width() // 2, mid_h - 3 * (mid_h // 5))
            )

        if self._err_msg:
            err_font = self.game.fonts["small"]
            err = err_font.render(self._err_msg, True, Color(RED))
            surface.blit(
                err,
                (mid_w - err.get_width() // 2, mid_h + 2 * mid_h // 5)
                )

        if self._remaining_lives <= 0:
            font = self.game.fonts["x_large"]
            game_over = font.render("GAME OVER", True, Color(RED))
            surface.blit(
                game_over,
                (mid_w - game_over.get_width() // 2, mid_h - 2 * (mid_h // 5))
                )

        if self._remaining_lives > 0:
            font = self.game.fonts["x_large"]
            win = font.render("WIN", True, Color(YELLOW))
            surface.blit(
                win,
                (mid_w - win.get_width() // 2, mid_h - 2 * (mid_h // 5))
                )
