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
pip install pygbag           # once
python3 -m pygbag --build web   # produces web/build/web/{index.html,web.apk,...}
```

## Run it locally

pygbag's own dev server sets the `Cross-Origin-Embedder-Policy` /
`Cross-Origin-Opener-Policy` headers the WASM runtime needs — a plain
`python -m http.server` will NOT work reliably. Use pygbag's server instead:

```bash
python3 -m pygbag web        # builds AND serves, then open the printed localhost URL
```

Open the browser's dev console while testing: any Python traceback (e.g. from
a real incompatibility in the shim or in `mazegenerator`) will print there.

## Deploying

Copy the contents of `web/build/web/` (after running the `--build` command
above) to your static host. **The host must send the same
`Cross-Origin-Embedder-Policy: require-corp` /
`Cross-Origin-Opener-Policy: same-origin` response headers**, or the WASM
Python runtime will fail to initialize. Confirm your host supports this
(e.g. via custom headers/`_headers` file) before relying on the deploy —
plain GitHub Pages does not let you set custom headers.

## What's verified vs. what still needs a real browser

Verified in this environment: `pygbag --build web` packages cleanly (73
files), and loading the built page in a headless, GPU-less browser fetches
and unpacks the app with no Python traceback or JS console error. What could
**not** be verified here (no GPU, and headless-Chromium-specific CORS/COEP
interactions with the CDN got in the way): that the game actually renders and
is playable end to end. Test that in a real desktop browser before shipping.
