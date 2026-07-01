*This activity has been created as part of the 42 curriculum by zadjerma, eielmini.*

# Pac-Man

## Description

A fully playable Pac-Man clone built in Python with Pygame. The player guides Pac-Man through procedurally generated mazes, eating pac-gums and avoiding four ghosts (Blinky, Pinky, Inky, and Clyde). Eating a super pac-gum temporarily frightens all ghosts, making them vulnerable. The game spans 10 progressively harder levels: mazes grow larger and ghosts become smarter with each level. A persistent leaderboard tracks the top scores across sessions.

- Per-level configuration (maze size, ghost types, strategy assignment)
- Persistent JSON-based highscore system with Pydantic validation
- Scene stack architecture (menu, play, pause, game-over, highscores, name entry)
- Projectile cheat (SPACE) and several hidden cheat codes

---

## Instructions

### Requirements

- Python 3.13+

### Quickstart (Makefile)

This project provides `make` targets that wrap the recommended workflow. From the project root run:

```bash
# Create the virtual environment and install dependencies
make install

# Run the game (passes config.json to the runner)
make run

# Run the game in the debugger
make debug

# Run lint checks (mypy + flake8)
make lint

# Run strict linting (strict mypy + flake8)
make lint-strict

# Clean generated caches and virtualenv
make clean
```

`make install` will ensure `uv` is available, create the local virtual environment, and synchronize dependencies declared in `pyproject.toml` (including the bundled `mazegenerator` wheel).


### Controls

| Key | Action |
|---|---|
| Arrow keys | Move Pac-Man |
| SPACE | Fire a missile (cheat) |
| ESC / BACKSPACE | Pause / return to menu |

---

## Configuration

The game is configured via a JSON file (default: `config.json`). The file is parsed and validated with Pydantic; invalid values will cause the game to exit with an error message.

### Top-level fields

| Field | Type | Default | Description |
|---|---|---|---|
| `highscore_filename` | string | — | Path to the highscores JSON file |
| `lives` | int ≥ 0 | `3` | Starting number of lives |
| `points_per_pacgum` | int > 0 | `10` | Points awarded per ordinary pac-gum |
| `points_per_super_pacgum` | int > 0 | `50` | Points awarded per super pac-gum |
| `points_per_ghost` | int > 0 | `200` | Base points awarded per ghost eaten |
| `seed` | int | `42` | Random seed passed to the maze generator |
| `level_max_time` | int > 0 | `90` | Time limit per level in seconds |
| `levels` | array | — | Ordered list of level descriptors (see below) |

### Level descriptor fields

```
{
  "id": 1,
  "width": 14,
  "height": 14,
  "ghosts": [
    { "type": "Blinky", "strategy": "euclidean" },
    { "type": "Pinky",  "strategy": "euclidean" },
    { "type": "Inky",   "strategy": "euclidean" },
    { "type": "Clyde",  "strategy": "euclidean" }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `id` | int ≥ 1 | Level identifier (informational) |
| `width` | int > 0 | Maze width in cells |
| `height` | int > 0 | Maze height in cells |
| `ghosts[].type` | string | Ghost name: `"Blinky"`, `"Pinky"`, `"Inky"`, or `"Clyde"` |
| `ghosts[].strategy` | string | Chase strategy: `"euclidean"` (default) or `"bfs"` |

The default `config.json` ships with 10 levels. Mazes grow from 14×14 to 21×12 cells, and ghost strategies escalate from all-Euclidean in level 1 to almost all-BFS by level 10.

---

## Highscore

### How it works

After every game (win or loss) the player is prompted to enter a name. The final score is appended to the leaderboard file (`highscores.json` by default). The leaderboard is a flat JSON array of `{ "name": string, "score": int }` objects; it is never sorted or trimmed on disk — all entries are preserved. When displayed in-game, the top 10 entries are selected by sorting on score descending at read time.

The current all-time highest score is shown on the HUD during gameplay (top-centre).

Note: the `highscores.json` file is stored in the user's local data directory:
`~/.local/share/pacman_game/highscores.json` (i.e. `Path.home() / ".local" / "share" / "pacman_game" / "highscores.json").

### Scoring rules

| Action | Points |
|---|---|
| Eat a pac-gum | `points_per_pacgum` (default 10) |
| Eat a super pac-gum | `points_per_super_pacgum` (default 50) |
| Eat a frightened ghost | 100 × 2^n (n = number of ghosts eaten in the current frightened chain) |
| Missile hits a ghost | 200 per ghost |
| Missile hits a pac-gum | Same as eating it directly |

### Why this design?

Storing every run in an append-only JSON file keeps the implementation simple and portable — no database dependency. Pydantic validates both the schema and field constraints (`min_length`, `ge=0`, etc.) when the file is loaded, so corrupted entries are rejected early. The file is re-read when the highscore screen is opened, ensuring scores added by the current session are immediately visible.

---

## Maze Generation

Mazes are generated using the **A-Maze-ing** package (`mazegenerator`), bundled as a local wheel (`mazegenerator-2.0.1-py3-none-any.whl`).

### Usage in the project

`LevelManager._load_maze()` constructs a new maze for each level:

```python
from mazegenerator.mazegenerator import MazeGenerator

self.maze = MazeGenerator(size=(width, height), seed=self.config.seed).maze
```

`MazeGenerator` returns a 2-D list of integers. Each cell value is a 4-bit bitmask encoding which walls are open: bit 0 = up, bit 1 = right, bit 2 = down, bit 3 = left (matching the `Directions` enum in `settings.py`).

After generation, `_break_wall()` manually clears cells on the leftmost and rightmost columns at the vertical midpoint to create the classic Pac-Man tunnel that wraps around the maze edges.

The same `seed` value is used across all levels, so the maze layout is deterministic for a given configuration — useful for reproducible playtesting. Changing `seed` in `config.json` produces entirely different mazes.

---

## Implementation

### Entry point and game loop

`pac-man.py` parses `sys.argv`, loads and validates `config.json` via `parser.load_config()`, instantiates `Game`, and calls `Game.run()`. The game loop runs at 60 FPS: it pumps Pygame events, delegates them to the active scene, calls `update()` on every stacked scene, calls `render()` on every stacked scene, then flips the display.

### Level progression

`LevelManager` owns the sequence of `LevelConfig` objects, the live maze grid, and all character sprites. When a level is cleared (all pac-gums eaten) or the time limit expires, it either calls `next_level()` to advance or routes to the end-game scene. Lives are tracked here; reaching zero lives triggers the game-over flow.

### Ghost AI

Ghost behaviour is split into two strategies via the **Strategy** pattern (`strategy.py`):

- **`EuclideanChaseStrategy`** — at each decision point the ghost enumerates walkable neighbours (excluding a U-turn), computes the Euclidean distance from each to the target cell, and picks the neighbour that minimises that distance. Fast and approximate.
- **`BFSChaseStrategy`** — runs a full breadth-first search from the ghost's current cell to the target and returns the first direction of the shortest path. Optimal but more expensive per frame.

Each ghost subclass defines its own `_target()` method (Blinky targets Pac-Man directly; Pinky targets 4 cells ahead; Inky uses a Blinky-relative offset; Clyde scatters when close). The active strategy is injected at construction time from the level config, so individual ghosts can use different strategies within the same level.

### Scoring chain for frightened ghosts

When Pac-Man eats a super pac-gum all ghosts enter frightened mode. Successive ghost kills within the same fright window double the reward: 200, 400, 800, 1600, … This multiplier resets when no ghosts remain frightened.

---

## General Software Architecture

The codebase is organized into a small, focused package under `src/` with a single top-level
runner `pac-man.py`. Responsibilities are split into game orchestration, scene UI, level
management, character implementations and utility modules.

- `pac-man.py` — entry point; parses args, loads config and starts `Game`.
- `src/pacman_game/game.py` — `Game` class: owns the Pygame display, clock, loaded assets,
	fonts, global score, and the `scenes_stack` used to route events, updates and rendering.
- `src/scenes/` — UI scenes (each scene implements `handle_events`, `update`, `render`):
	- `scene.py` — base `Scene` class with enter/exit helpers
	- `menu_scene.py` — main menu and navigation
	- `play_scene.py` — active gameplay, HUD and input handling
	- `pause_scene.py` — pause overlay and resume/quit
	- `end_game.py` — game-over / win summary
	- `highscore_scene.py` — top-10 leaderboard display
	- `name_input_scene.py` — player name entry after a run
	- `instructions_scene.py` — controls and README display

- `src/pacman_game/level_manager.py` — builds and holds the live maze, spawns characters and
	manages per-level state and progression.
- `src/characters/` — character implementations and behaviours:
	- `character.py` — abstract movement/collision helpers used by all characters
	- `pacman.py` — player-controlled Pac-Man (movement, shooting, death)
	- `ghosts.py` — ghost subclasses (Blinky/Pinky/Inky/Clyde) and AI hooks
	- `missile.py` — missile projectile used by the cheat

- `src/strategy.py` — chase strategies (Euclidean / BFS) injected into ghosts.
- `src/pacman_game/parser.py` — Pydantic models and helpers for loading/saving `config.json`
	and `highscores.json`.
- `src/pacman_game/settings.py` — constants (screen size, tile size, FPS, colors, enums).
- `src/pacman_game/spritesheet.py` — helper to slice sprite atlas PNGs into surfaces.
- `src/pacman_game/maze_drawing.py` — utilities to translate maze bitmask into renderable tiles.
- `src/pacman_game/pacgum.py` — pac-gum placement and management.

Key relationships:

- `Game` manages the scene stack: the top scene receives input while all scenes are rendered
	(allowing overlays like pause to draw on top of play).
- `PlayScene` delegates level-specific work to `LevelManager`, which owns `Pacman` and the
	`pygame.sprite.Group` of ghosts and pac-gums.
- Ghost AI is implemented via the Strategy pattern; each ghost holds a strategy object that
	defines its chase behaviour.
- `parser.py` is the single filesystem-facing module (configs and highscores); other modules
	operate on validated domain objects.

---

## Project Management

The project was developed iteratively, starting with core mechanics (maze rendering, Pac-Man movement) and progressively adding ghost AI, scene management, levels, and polish. Branches were used per feature (`scene`, `scenes`), merged into `main` via pull requests.

---

## Resources

### Documentation and references

- [Ghosts AI](https://www.youtube.com/watch?v=ataGotQ7ir8)
- [Pygame documentation](https://www.pygame.org/docs/)
- [Pydantic v2 documentation](https://docs.pydantic.dev/latest/)
- [The Pac-Man Dossier — ghost AI mechanics](https://pacman.holenet.info/) — Jamey Pittman's in-depth analysis of original Pac-Man ghost behavior
- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [BFS — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [uv — Python package manager](https://docs.astral.sh/uv/)

### AI usage

Ai was used for
- **README writing**: this file was drafted with AI assistance.
- **Pattern design**: how to design the architecture of the scenes to set a maintanable code.
- **Debugging**
