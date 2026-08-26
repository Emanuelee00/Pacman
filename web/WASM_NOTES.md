# Pacman in the browser: what WASM is, what broke, and how it got fixed

## What "WASM" actually is

WebAssembly (WASM) is a low-level bytecode format that every major browser
(Chrome/Edge's V8 engine, Firefox's SpiderMonkey, Safari's JavaScriptCore)
can run at near-native speed. It's not JavaScript — it's a compilation
*target*, the same way x86 machine code is a target for C. You compile some
other language down to `.wasm`, ship that file to the browser, and the
browser's JS engine JIT-compiles it to real machine code on the fly, inside
a memory-sandboxed VM (a single contiguous block of linear memory the WASM
code cannot escape).

This project uses **Pygbag** + **Emscripten** to get there:

- Emscripten is a full toolchain that compiles C/C++ (and, via a custom
  CPython build, actual CPython itself) to WASM, plus a compatibility layer
  that reimplements POSIX-ish things (files, threads, sockets) on top of
  browser primitives.
- Pygbag builds on that: it ships a prebuilt CPython 3.12 + SDL2 WASM
  runtime, packages a Python app's source as a data blob next to it, and
  provides a bootstrap (`main.js` / `site.py`) that: unpacks the app,
  resolves any extra pure-Python or WASM-native dependencies (numpy, PIL,
  **pygame itself**) from a package CDN at *runtime* (not build time), then
  runs `main.py` inside an asyncio event loop (the browser event loop won't
  let anything block it, so pygbag turns the game loop into `async def
  main()` + `await asyncio.sleep(0)` per frame).
- SDL2, compiled the same way, creates a window that's actually an HTML5
  `<canvas>` element and draws into it via either the canvas 2D API or
  WebGL, depending on how the app opened its display.

So "how does Google do it" — Chrome's V8 engine has a WASM compiler
built in (Liftoff for fast startup, TurboFan for hot-path optimization,
same tiering strategy V8 uses for JS). It's not a plugin or an extension;
it's a standard part of the browser, sandboxed the same way a normal tab is.

## The actual bug (root cause)

`web/main.py` never declared `pygame` as a dependency. Pygbag resolves
runtime dependencies through an ad hoc convention: a
[PEP 723](https://peps.python.org/pep-0723/) inline metadata block at the
top of the entry script:

```python
# /// script
# dependencies = [
#   "pygame.base",
# ]
# ///
```

Without it, pygbag's dependency resolver never tries to fetch anything.
Critically, that *didn't* fail loudly: pygbag's base CPython/Emscripten
image already ships an **empty namespace package** called `pygame`
(a directory with no files in it, there purely so `import pygame`
doesn't explode before the real wheel is installed). So `import pygame`
silently "succeeded" with a stub exposing nothing, and the game crashed
several frames later and one file away, deep in `menu_scene.py`, with:

```
ImportError: cannot import name 'Color' from 'pygame' (unknown location)
```

That's a classically misleading error — it looks like a `pygame`
version/API problem, not a "dependency never got installed" problem. Every
earlier debugging session chased that misdirection: canvas visibility,
ports, audio unlock gestures, a hand-built static `pygame.so` — all real
things to check for a blank-screen WASM game, none of them the actual
cause here.

One more wrinkle, found while fixing this: the dependency name has to be
literally `pygame.base`, not `pygame`. Pygbag's resolver checks
`importlib.util.find_spec("pygame")` to decide whether a wheel install is
needed, and that check *also* finds the same empty stub package, so a
plain `"pygame"` dependency gets silently treated as "already satisfied" and
skipped. `pygame.base` is special-cased in pygbag's resolver specifically to
bypass that check and force the real `pygame-ce` wheel to download.

## The red herring layered on top

An earlier session, seeing a blank canvas, correctly reasoned that pygame's
Emscripten SDL2 build sometimes renders to a WebGL-backed `<canvas>`
(commonly `#canvas3d`) rather than the plain 2D one pygbag shows by default,
and wrote a JS-interop shim to swap which canvas was visible. That's a real
phenomenon in pygbag apps — just not this one. This game calls
`pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))` with no `OPENGL`
flag, so SDL renders through the plain 2D canvas. The shim was hiding the
canvas the game actually draws to and showing an empty WebGL one instead —
harmless once pygame loaded for real, but one more thing that looked like
part of the problem and wasn't. It's been removed.

## What was actually changed

1. Added the PEP 723 `pygame.base` dependency block to `web/main.py`
   (the real fix).
2. Removed the canvas-swapping JS shim from `web/main.py` (unnecessary —
   see above).
3. Deleted a leftover statically-compiled `pygame` `.so` experiment from
   `web/vendor/` that was fighting the dynamic wheel and breaking every
   pygame submodule with `PyModule_AddObjectRef()` errors.
4. Confirmed pygbag's dev server hardcodes its package CDN to
   `localhost:8000` unless the page URL carries `?PYGPI=<origin>/cdn/` —
   the custom `web/pygbag.tmpl` already adds that, which is why package
   downloads correctly land on port 8020 instead. Port 8000 stays off
   limits because an unrelated Docker service already owns it on this
   machine.

Verified end to end with a headless browser: page load → wheel download
(HTTP 200 from `localhost:8020`) → pygame-ce initializes → menu renders →
gameplay renders (maze, Pac-Man, all four ghosts, the pacgum dots, score/
lives/level HUD).

## Does saved data (highscores) actually persist?

Yes. `pacman.parser` branches on `sys.platform == "emscripten"` to read/write
highscores through the browser's `localStorage` instead of a JSON file
(there's no filesystem to persist in the browser). `localStorage` is
standard, origin-scoped browser storage — confirmed by directly writing a
value, reloading the page, and opening a fresh tab: the value was still
there every time. It behaves exactly like any website's local storage:

- Tied to the exact origin (`http://localhost:8020` here — a different
  port or host is a different, empty storage bucket).
- Survives page reloads and full browser restarts.
- Cleared only if the user clears site data/browsing data for that origin,
  or browses in a private/incognito window.
