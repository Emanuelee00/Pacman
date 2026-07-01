"""Scene for the main gameplay."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, cast
import pygame
from pygame import Color
from pacman.characters.pacman import Pacman
from pacman.level_manager import LevelManager
from pacman.settings import (
    WALL_SIZE,
    CELL_SIZE,
    OFFSET_Y,
    CHEAT_LIVES,
    CHEAT_42,
    LEVEL_CHEAT,
    UNCHEAT,
    SCREEN_MARGIN,
    DURATION,
    YELLOW,
    WHITE,
    RED,
    GREEN,
)
from pacman.maze_drawing import draw_maze, to_tile_map
from .scene import Scene

if TYPE_CHECKING:
    from pacman.game import Game
    from pacman.characters.ghosts import Ghost
    from pygame import Surface


class PlayScene(Scene):
    """Class representing the play scene."""

    def __init__(self, game: Game) -> None:
        """Initialize the play scene state.

        Args:
            game: Reference to the main Game object.
        """
        super().__init__(game)

        # Setup level manager and load first level
        self.level_manager: LevelManager = LevelManager(
            game.config, game.assets
            )
        self.level_manager.load_level()
        self.maze: list[list[int]] = self.level_manager.maze
        self._load_tile_map()
        draw_maze(
            self._maze_surface,
            self._tilemap,
            self.maze,
            self.game.assets["maze_tiles"])
        self._maze_surface_base: Surface = self._maze_surface.copy()
        self._set_canvas()

        # Game state variables
        self._remaining_lives = game.config.lives
        self._game_started: bool = False
        self._waiting: bool = False
        self._waiting_start: int = pygame.time.get_ticks()
        self._duration: int = DURATION
        self._game_timer: float = self._duration
        self._last_tick: int = pygame.time.get_ticks()
        self._death_time: int = 0
        self._time_out: bool = False
        self._hits_frightened: int = 1
        self._cheat_time: int = 0
        self._dead_ghosts: list[tuple[Ghost, int]] = []

        # Cheat mode attributes
        self._key_buffer: list[int] = []
        self._key_buffer2: list[int] = []
        self._rainbow_active: bool = False
        self._rainbow_hue: float = 0.0

    def _load_tile_map(self) -> None:
        """Convert the maze layout into a tile map, create the maze surface."""
        tilemap_w = WALL_SIZE + CELL_SIZE * len(self.maze[0])
        tilemap_h = WALL_SIZE + CELL_SIZE * len(self.maze)
        self._maze_surface = pygame.Surface((tilemap_w, tilemap_h))

        self._tilemap = to_tile_map(self.maze)
        self._tilemap_size = (tilemap_w, tilemap_h)

    def _set_canvas(self) -> None:
        """Set up the game canvas based on the tile map size."""
        tilemap_w, tilemap_h = self._tilemap_size
        self._game_canvas = pygame.Surface((
            tilemap_w,
            tilemap_h + 2 * OFFSET_Y,
        ))

    @property
    def pacman(self) -> Pacman:
        """Get the Pacman character from the level manager."""
        return self.level_manager.pacman

    @property
    def ghosts(self) -> pygame.sprite.Group[Any]:
        """Get the group of ghost sprites."""
        return self.level_manager.ghosts

    @property
    def pacgums(self) -> pygame.sprite.Group[Any]:
        """Get the group of pacgum sprites."""
        return self.level_manager.pacgums

    @property
    def missiles(self) -> pygame.sprite.Group[Any]:
        """Get the group of missile sprites."""
        return self.level_manager.missiles

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle incoming Pygame events.

        Args:
            events: List of Pygame events.
        """
        from .pause_scene import PauseScene
        for event in events:
            if event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_BACKSPACE
                    or event.key == pygame.K_ESCAPE
                ):
                    PauseScene(self.game).enter_scene()

                self._key_buffer.append(event.key)
                self._key_buffer2 = (
                    self._key_buffer[-max(len(CHEAT_42), len(UNCHEAT)):]
                )
                if self._key_buffer[-len(CHEAT_LIVES):] == CHEAT_LIVES:
                    self._cheat_time = pygame.time.get_ticks()
                    self.pacman.set_cheated()

                if self._key_buffer2[-len(CHEAT_42):] == CHEAT_42:
                    self._rainbow_active = True

                if self._key_buffer[-len(UNCHEAT):] == UNCHEAT:
                    self.pacman.set_normal()
                    self._rainbow_active = False

                if (
                    len(self._key_buffer) >= 1
                    and self._key_buffer[-1] in LEVEL_CHEAT
                ):
                    if self._key_buffer[-1] == pygame.K_KP0:
                        self.level_manager.current_index = 9
                        self._reset(new_level=True)
                    else:
                        self.level_manager.current_index = LEVEL_CHEAT.index(
                            self._key_buffer[-1]
                            )
                        self._reset(new_level=True)

                if event.key == pygame.K_SPACE:
                    self.pacman.shoot(
                        self.missiles, self.game.assets["missile_sprites"]
                        )

                if len(self._key_buffer) > max(len(CHEAT_LIVES), len(UNCHEAT)):
                    self._key_buffer.pop(0)

    def _redraw_maze(self) -> None:
        """Redraw the maze surface with a rainbow color effect."""
        def rainbow_color(self: PlayScene) -> tuple[int, int, int]:
            c = pygame.Color(0, 0, 0)
            c.hsva = (self._rainbow_hue, 100, 100, 100)
            return (c.r, c.g, c.b)

        color = rainbow_color(self)
        self._maze_surface.fill((0, 0, 0))
        pygame.transform.threshold(
            self._maze_surface,
            self._maze_surface_base,
            (0, 0, 0),
            (5, 5, 5, 0),
            color,
            1,
            None,
            True,
        )

    def _render_rainbow(self) -> None:
        """Render the maze with a rainbow effect."""
        self._rainbow_hue = (self._rainbow_hue + 2) % 360
        self._redraw_maze()

    def _start_waiting(self) -> None:
        """Start a waiting period."""
        if not self._waiting:
            self._waiting = True
            self._waiting_start = pygame.time.get_ticks()

    def _check_waiting(self, duration: int) -> bool:
        """
        Check if the waiting period (duration) has elapsed.

        Args:
            duration: Duration in milliseconds to check against.
        Returns:
            True if the waiting period has elapsed, False otherwise.
        """
        if not self._waiting:
            return False
        if pygame.time.get_ticks() - self._waiting_start >= duration:
            self._waiting = False
            return True
        return False

    def _handle_pacgum_collisions(self) -> None:
        """
        Check for collisions between Pacman and pacgums.

        Update score and ghost states.
        """
        hits = pygame.sprite.spritecollide(
            cast(Any, self.pacman), self.pacgums, True
            )
        for hit in hits:
            if hit.is_super:
                self.game.score += self.game.config.points_per_super_pacgum
                for ghost in self.ghosts:
                    ghost.is_frightened = True
                    ghost.direction = ghost._opposite_direction(
                        ghost.direction
                        )
            else:
                self.game.score += self.game.config.points_per_pacgum

    def _handle_ghost_collisions(self) -> None:
        """
        Check for collisions between Pacman and ghosts.

        Update score, ghost states, and player lives accordingly.
        """
        for ghost in self.ghosts:
            if (
                self.pacman.is_alive and ghost.is_alive
                and ghost.rect.collidepoint(
                    self.pacman.rect.centerx,
                    self.pacman.rect.centery,
                )
            ):

                if ghost.is_frightened:
                    self._hits_frightened *= 2
                    self.game.score += 100 * self._hits_frightened
                    self._dead_ghosts.append(
                        (ghost, self._hits_frightened * 100)
                        )
                    if self._hits_frightened == 16:
                        self._hits_frightened = 1
                    ghost.is_alive = False
                    ghost.is_visible = False
                    self._start_waiting()
                else:
                    self._remaining_lives -= 1
                    self.pacman.set_death()
                    self._start_waiting()

        if not any(ghost.is_frightened for ghost in self.ghosts):
            self._hits_frightened = 1

    def _handle_ghost_death(self) -> None:
        """
        Handle the respawn of ghosts that have been eaten by Pacman.

        Ghosts will respawn after a delay.
        The player will earn points for each ghost eaten.
        """
        for ghost, _ in self._dead_ghosts:
            self._start_waiting()
            if self._check_waiting(2000) is True:
                ghost.respawn()
                self._dead_ghosts.pop(0)
                ghost.is_alive = True
                ghost.is_visible = True
                ghost.is_frightened = False

    def _handle_pacman_death(self) -> None:
        """
        Handle the death of Pacman.

        Pacman will respawn after a delay if lives remain.
        """
        if not self.pacman.is_alive:
            self._start_waiting()

            if self._check_waiting(2000) is True:
                self.pacman.start_dying = True
                for ghost in self.ghosts:
                    ghost.is_visible = False

        if self.pacman.death_finished:
            self.pacman.respawn()
            self.pacman.is_blocked = False
            for ghost in self.ghosts:
                ghost.respawn()
            self._start_waiting()
            self._game_started = False

    def _handle_missile_collisions(self) -> None:
        """
        Check for collisions between missiles and ghosts or pacgums.

        Update score, ghost states, and remove missiles and pacgums as needed.
        """
        alive_ghosts: pygame.sprite.Group[Any] = pygame.sprite.Group()
        for ghost in self.ghosts:
            if ghost.is_alive:
                alive_ghosts.add(ghost)

        for missile in self.missiles:
            hit_ghosts = pygame.sprite.spritecollide(
                missile,
                alive_ghosts, False
                )
            if hit_ghosts:
                missile.kill()
                for ghost in hit_ghosts:
                    self._hits_frightened *= 2
                    self.game.score += 100 * self._hits_frightened
                    self._dead_ghosts.append(
                        (ghost, self._hits_frightened * 100)
                        )
                    if self._hits_frightened == 16:
                        self._hits_frightened = 1
                    ghost.is_alive = False
                    ghost.is_visible = False
                    self._start_waiting()
            for hit in pygame.sprite.spritecollide(
                missile, self.pacgums, True
            ):
                if hit.is_super:
                    self.game.score += self.game.config.points_per_super_pacgum
                else:
                    self.game.score += self.game.config.points_per_pacgum

    def _reset(self, new_level: bool = False) -> None:
        """
        Reset the game state for a new level or after losing a life.

        Args:
            new_level (bool): Whether to remove a life from the player.
        """
        self.level_manager.load_level()
        self._dead_ghosts = []
        self.maze = self.level_manager.maze
        self._load_tile_map()
        draw_maze(
            self._maze_surface,
            self._tilemap,
            self.maze,
            self.game.assets["maze_tiles"])
        self._maze_surface_base = self._maze_surface.copy()
        self._set_canvas()
        self._game_timer = self._duration
        self._game_started = False

        if new_level is False:
            self._remaining_lives -= 1

    def _check_endgame(self) -> None:
        """Check if the game has ended due to losing all lives."""
        if self._remaining_lives == 0:
            self.exit_scene()
            from .end_game import EndgameScene
            EndgameScene(
                self.game, self._remaining_lives
                ).enter_scene()

    def _check_endlevel(self) -> None:
        """Check if the current level has been completed."""
        if len(self.pacgums) == 0:
            if self.level_manager.next_level():
                self._reset(new_level=True)
            else:
                from .end_game import EndgameScene
                EndgameScene(
                    self.game, self._remaining_lives
                ).enter_scene()

    def _check_timeout(self) -> None:
        """Check if the game timer has run out and handle the timeout state."""
        if self._game_timer <= 500:
            self._game_timer = 0
            self._start_waiting()
            self._time_out = True
            if self._check_waiting(1000) is True:
                self._time_out = False
                self._remaining_lives -= 1
                self.pacman.respawn()
                for ghost in self.ghosts:
                    ghost.respawn()
                self._game_started = False
                self._game_timer = self._duration

    def _update_characters(self) -> None:
        """Update the state of all characters in the game."""
        self.pacman.next_direction = pygame.key.get_pressed()
        self.pacman.update()
        self.ghosts.update()
        self.pacgums.update()
        self.missiles.update()

        if self.pacman._cheated:
            for ghost in self.ghosts:
                ghost.is_frightened = True

    def update(self) -> None:
        """Update the game state, character updates and game logic checks."""
        self._check_endgame()
        self._check_endlevel()
        if not self._game_started:
            self._start_waiting()
            if self._check_waiting(2000) is True:
                self._game_started = True
        else:
            if self.pacman.is_alive and not self._time_out:
                self._game_timer = max(0, self._game_timer - self.game.dt)
            if not self._time_out:
                self._update_characters()
                self._handle_pacgum_collisions()
                self._handle_ghost_collisions()
                self._handle_ghost_death()
                self._handle_pacman_death()
                self._handle_missile_collisions()
            self._check_timeout()

    def _display_info(self) -> None:
        """
        Display game information.

        Shows points, high score, time, lives, and level on the game canvas.
        """
        font = self.game.fonts["small"]

        # Top left: POINTS
        points_label = font.render("1UP", True, Color(YELLOW))
        points_val = font.render(str(self.game.score), True, Color(WHITE))
        self._game_canvas.blit(points_label, (0, 0))
        self._game_canvas.blit(points_val, (0, 35))

        # Top center: HIGH SCORE
        hs_label = font.render("HIGH SCORE", True, Color(YELLOW))
        if self.game.high_score is not None:
            hs_val = font.render(
                str(self.game.high_score.name)
                + " : " + str(self.game.high_score.score), True, Color(WHITE)
            )

        else:
            hs_val = font.render("0", True, Color(WHITE))
        cx = self._game_canvas.get_width() // 2
        self._game_canvas.blit(hs_label, (cx - hs_label.get_width() // 2, 0))
        self._game_canvas.blit(hs_val, (cx - hs_val.get_width() // 2, 35))

        # Top right: TIME
        time_label = font.render("TIME", True, Color(YELLOW))
        time_val = font.render(
            f"{self._game_timer // 1000 // 60:02}:"
            f"{self._game_timer // 1000 % 60:02}", True, Color(WHITE)
            )
        self._game_canvas.blit(
            time_label,
            (self._game_canvas.get_width() - time_label.get_width(), 0)
            )
        self._game_canvas.blit(
            time_val,
            (self._game_canvas.get_width() - time_val.get_width(), 35)
            )

        # Bottom left: LIVES
        cy = self._game_canvas.get_height() - OFFSET_Y // 2
        lives_label = font.render("LIVES", True, Color(YELLOW))
        self._game_canvas.blit(
            lives_label, (0, cy - lives_label.get_height() // 2))
        for i in range(self._remaining_lives):
            pygame.draw.circle(
                self._game_canvas,
                Color(YELLOW), (lives_label.get_width() + 30 + i * 30, cy), 8
                )

        # Bottom right: LEVEL
        l_label = font.render(
            f"LEVEL {self.level_manager.current_index + 1}",
            True,
            Color(YELLOW)
            )
        self._game_canvas.blit(
            l_label,
            (
                self._game_canvas.get_width() - l_label.get_width(),
                cy - l_label.get_height() // 2
            )
        )

    def render(self, surface: Surface) -> None:
        """Render the game state onto the given surface.

        Args:
            surface: The Pygame surface to render the game onto.
        """
        self._game_canvas.fill((0, 0, 0))
        self._game_canvas.blit(self._maze_surface, (0, OFFSET_Y))

        if self._time_out:
            self.game.draw_text(
                self._game_canvas,
                "TIME OUT!",
                Color(RED),
                self._game_canvas.get_width() // 2,
                self._game_canvas.get_height() // 2 + OFFSET_Y // 2,
                size="x_large"
            )

        if not self._game_started:
            self.game.draw_text(
                self._game_canvas,
                "READY!",
                Color(RED),
                self._game_canvas.get_width() // 2,
                self._game_canvas.get_height() // 2 + OFFSET_Y // 2,
                size="x_large"
            )

        for pacgum in self.pacgums:
            if pygame.time.get_ticks() // 300 % 2 == 0 and pacgum.is_super:
                continue
            else:
                self._game_canvas.blit(
                    pacgum.image,
                    (pacgum.rect.x, pacgum.rect.y + OFFSET_Y)
                )

        if self.pacman.is_visible:
            self._game_canvas.blit(
                self.pacman.image,
                (self.pacman.rect.x, self.pacman.rect.y + OFFSET_Y),
            )

        for ghost in self.ghosts:
            if ghost.is_visible:
                self._game_canvas.blit(
                    ghost.image,
                    (ghost.rect.x, ghost.rect.y + OFFSET_Y),
                )

        for ghost, points in self._dead_ghosts:
            x, y = ghost.rect.center
            self.game.draw_text(
                self._game_canvas,
                str(points),
                Color(GREEN),
                x,
                y + OFFSET_Y,
                size="x_small"
                )

        for missile in self.missiles:
            self._game_canvas.blit(
                missile.image,
                (missile.rect.x, missile.rect.y + OFFSET_Y)
            )

        self._display_info()

        # Cheat message:
        if (
            self._cheat_time
            and pygame.time.get_ticks() - self._cheat_time < 1000
        ):
            cheat_font = self.game.fonts["x_large"]
            l1 = cheat_font.render("FOR THE", True, Color(RED))
            l2 = cheat_font.render("FAMILY", True, Color(RED))
            self._game_canvas.blit(
                l1,
                (
                    self._game_canvas.get_width() // 2 - l1.get_width() // 2,
                    self._game_canvas.get_height() // 2 - l1.get_height()
                )
            )
            self._game_canvas.blit(
                l2,
                (
                    self._game_canvas.get_width() // 2 - l2.get_width() // 2,
                    self._game_canvas.get_height() // 2
                )
            )
        else:
            self._cheat_time = 0

        canvas_w, canvas_h = self._game_canvas.get_size()
        surface_w, surface_h = surface.get_size()

        avail_w = surface_w * (1 - 2 * SCREEN_MARGIN)
        avail_h = surface_h * (1 - 2 * SCREEN_MARGIN)

        scale = min(avail_w / canvas_w, avail_h / canvas_h)

        scaled_size = (
            max(1, int(round(canvas_w * scale))),
            max(1, int(round(canvas_h * scale))),
        )

        if scaled_size == (canvas_w, canvas_h):
            canvas_to_draw = self._game_canvas
        else:
            canvas_to_draw = pygame.transform.scale(
                self._game_canvas,
                scaled_size,
            )

        left = (surface_w - scaled_size[0]) // 2
        top = (surface_h - scaled_size[1]) // 2

        surface.blit(canvas_to_draw, (left, top))

        if self._rainbow_active:
            self._render_rainbow()
        else:
            self._maze_surface.fill((0, 0, 0))
            self._maze_surface.blit(self._maze_surface_base, (0, 0))
