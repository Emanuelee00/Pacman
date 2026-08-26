# Pacman — Web (WASM) build

Browser build of the game via [pygbag](https://github.com/pygame-web/pygbag), which
compiles pygame apps to WebAssembly (Python compiled with Emscripten + SDL, the
same technology stack browsers use to run native code on the web).

## Why this folder exists, and what's different from the desktop build

pygbag packages whatever is inside this folder as-is — it does not resolve
dependencies from PyPI. So everything the game needs has to physically live
here:

- `pacman/` and `config.json` are **copied in by `build.sh`** from `../src/pacman`
  and `../config.json` — they are not duplicated by hand and are gitignored,
  so the desktop sources stay the single source of truth.
- `vendor/mazegenerator/` is **extracted from the project's wheel** by
  `build.sh` (also gitignored). It's pure Python, so it runs in WASM unchanged.
- `vendor/pydantic/` is a **hand-written, WASM-only stand-in for pydantic**
  (committed to git). Real pydantic v2 depends on `pydantic-core`, a compiled
  Rust extension with no Emscripten build published on PyPI, so it cannot run
  in the browser. This shim implements just the subset of pydantic's API that
  `pacman.parser` uses (`BaseModel`, `Field`, `ConfigDict`, `field_validator`,
  `ValidationError`) — `pacman/parser.py` itself is unchanged. The desktop
  build keeps depending on real pydantic; this shim only ever ships here.
- Highscore persistence: on desktop, `pacman.parser` writes to
  `~/.local/share/pacman_game/highscores.json`. There is no such filesystem in
  the browser, so `pacman/parser.py` branches on `sys.platform == "emscripten"`
  and uses the browser's `localStorage` instead (via pygbag's `platform.window`
  JS bridge). Same file, same functions, one small branch.

## Build

From the repo root:

```bash
web/build.sh                 # sync src/pacman, config.json, mazegenerator into web/
uv tool install pygbag       # once
make web-build               # produces web/build/web/{index.html,web.apk,...}
```

## Run it locally

pygbag's own dev server sets the `Cross-Origin-Embedder-Policy` /
`Cross-Origin-Opener-Policy` headers the WASM runtime needs — a plain
`python -m http.server` will NOT work reliably. Use pygbag's server instead:

```bash
make web-run                  # serves on http://localhost:8020
```

Click the start prompt shown by Pygbag before the game opens. Browsers require
this user interaction before SDL is allowed to initialize audio.

The build is pinned to Pygbag 0.9.3. Its current template references a missing
`browserfs.min.js`, so the local template loads that runtime dependency from
Pygbag's stable 0.9 archive.

Pygbag's runtime hardcodes its package CDN to `localhost:8000` whenever the
page is served from any `localhost:8xxx` origin, unless the page URL carries a
`?PYGPI=<origin>/cdn/` query param — the local template adds that so package
downloads correctly target port 8020 instead (port 8000 on this machine is
already used by an unrelated Docker service, so pygbag can't just bind there).

`web/main.py` also needs a PEP 723 dependency block declaring `pygame.base`
(not `pygame`) at the very top of the file:

```python
# /// script
# dependencies = [
#   "pygame.base",
# ]
# ///
```

Without it, pygbag never fetches the pygame-ce wheel: an empty `pygame`
namespace package already exists in the base runtime, so `import pygame`
"succeeds" with a stub missing everything (`Color`, `Rect`, `Surface`, ...)
instead of raising an import error. The dependency name has to be
`pygame.base`, not `pygame` — pygbag's resolver treats a bare `pygame` as
already satisfied by that same stub and never downloads the real wheel.

Open the browser's dev console while testing: any Python traceback (e.g. from
a real incompatibility in the shim or in `mazegenerator`) will print there.

`make run` is the native desktop build and requires a graphical display on the
same machine. On a headless remote server, use `make web-run` instead.

## Deploying

Copy the contents of `web/build/web/` (after running the `--build` command
above) to your static host — any plain static file server works, no special
response headers required. (This game doesn't use SDL threads/
`SharedArrayBuffer` — `pthreads=False` at runtime — so don't set
`Cross-Origin-Embedder-Policy: require-corp` on the host: it forces the
browser to block the cross-origin `pythons.js`/`main.js`/wheel fetches from
pygame-web's CDN unless that CDN also sends a matching CORP header, which it
doesn't. `web/pygbag.tmpl`'s local-dev-only CDN proxying is what avoids this
for `make web-run`; a plain deploy has no such proxy, so it must stay
same-origin-header-free instead.)

Deployed and verified working end to end at
https://pacman.92-4-217-42.sslip.io — a multi-stage Docker image (`uv`-based
build stage runs `pygbag --build web`, then plain `nginx:alpine` serves the
output), defined outside this repo in the portfolio's deploy platform.

## What's verified

Verified end to end in this environment, including actual rendering: loading
the served page in a headless browser, clicking the start prompt, downloading
the pygame-ce wheel, and reaching a playable frame (menu screen and in-maze
gameplay both confirmed via screenshot — maze, Pac-Man, ghosts, and pacgums
all draw correctly). Still worth a spot check in a real desktop browser
before shipping, mainly for audio and input feel.
