#!/usr/bin/env bash
# Sync the game source + mazegenerator wheel into web/ before a pygbag build.
# pygbag packages the given folder as-is (no PyPI dependency resolution), so
# everything the web build needs must physically live inside web/. This
# script keeps src/pacman and config.json as the single source of truth and
# copies them in fresh; only main.py and vendor/pydantic are web-specific
# and live only here.
set -euo pipefail
cd "$(dirname "$0")"

rm -rf pacman vendor/mazegenerator
cp -r ../src/pacman pacman
cp ../config.json config.json

python3 -m zipfile -e ../mazegenerator-2.0.1-py3-none-any.whl vendor/_mazegenerator_wheel
mv vendor/_mazegenerator_wheel/mazegenerator vendor/mazegenerator
rm -rf vendor/_mazegenerator_wheel

echo "web/ synced. Build with: pygbag --build web   (run from the repo root)"
