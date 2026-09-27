"""Fail closed when CG entrances, Godot packs, or refresh guards drift."""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://gouchin0326-source.github.io/codex-mobile-gate"
GAMES = ("gravity-canvas", "genre-lab-3d", "sky-spire", "neon-sequence", "orb-collector", "blade-arena")
PACKS = {"gravity-canvas": "index-v147.pck", "genre-lab-3d": "index-v1.pck", "sky-spire": "index-v1.pck", "neon-sequence": "index-v1.pck", "orb-collector": "index-v1.pck", "blade-arena": "index-v3.pck"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def version(html, route):
    match = re.search(r'serviceWorker\.register\("sw\.js\?v=([^"&]+)', html)
    require(match, f"{route}: service worker version missing")
    return match.group(1)


def check_html(html, route, prefix):
    require('data-tab="godot"' in html and 'id="tab-godot"' in html, f"{route}: GODOT tab missing")
    require('id="godot-game-list"' in html, f"{route}: game list missing")
    require('id="godot-frame"' not in html, f"{route}: direct-launch frame returned")
    for game in GAMES:
        require(f'data-godot-game="{game}"' in html, f"{route}: {game} icon missing")
        require(f'data-godot-detail="{game}"' in html, f"{route}: {game} detail missing")
        require(f'data-src="{prefix}projects/{game}/index.html?' in html, f"{route}: {game} iframe route wrong")
    require('if (!frame.src) frame.src = frame.dataset.src' in html, f"{route}: click-to-load missing")
    return version(html, route)


def local_check():
    versions = []
    caches = []
    for route, folder, prefix, cache_prefix in (
        ("root", ROOT, "./latest/", "codex-gate-root-"),
        ("latest", ROOT / "latest", "./", "codex-gate-latest-"),
    ):
        html = (folder / "index.html").read_text(encoding="utf-8")
        current = check_html(html, route, prefix)
        versions.append(current)
        require(f'manifest.webmanifest?v={current}' in html, f"{route}: manifest link stale")
        manifest = json.loads((folder / "manifest.webmanifest").read_text(encoding="utf-8"))
        require(f"?v={current}" in manifest["start_url"], f"{route}: PWA start URL stale")
        sw = (folder / "sw.js").read_text(encoding="utf-8")
        cache = re.search(r'const CACHE = "([^"]+)"', sw)
        require(cache and cache.group(1).startswith(cache_prefix), f"{route}: cache namespace wrong")
        require(f'key.startsWith("{cache_prefix}")' in sw, f"{route}: deletes another SW cache")
        require('cache: "no-store"' in sw, f"{route}: document cache can hide latest")
        caches.append(cache.group(1))
    require(len(set(versions)) == 1 and len(set(caches)) == 2, "entrance versions or caches diverged")
    for game, pack in PACKS.items():
        folder = ROOT / "latest" / "projects" / game
        html = (folder / "index.html").read_text(encoding="utf-8")
        require(f'"mainPack":"{pack}"' in html, f"{game}: versioned pack not selected")
        require((folder / pack).is_file(), f"{game}: pack missing")
    refresh = Path("C:/Codex/scripts/run-cg-refresh.ps1")
    if refresh.is_file():
        source = refresh.read_text(encoding="utf-8")
        require("robocopy" not in source.lower(), "refresh can overwrite UI from stale checkout")
        require("& $GitExe -C $RefreshRepo add -- $paths" in source, "refresh is not data-only")
        require("& $GitExe -C $RefreshRepo add -- index.html" not in source, "refresh stages root UI")
    return versions[0]


def fetch(path):
    request = urllib.request.Request(f"{SITE}/{path}", headers={"Cache-Control": "no-cache", "User-Agent": "CG-Entry-Check/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        require(response.status == 200, f"public {path}: HTTP {response.status}")
        return response.read().decode("utf-8")


def public_check(expected):
    for route, path, prefix in (
        ("root", "index.html", "./latest/"),
        ("latest", "latest/index.html", "./"),
    ):
        html = fetch(f"{path}?verify={expected}")
        require(check_html(html, route, prefix) == expected, f"public {route}: old version")
    for game, pack in PACKS.items():
        html = fetch(f"latest/projects/{game}/index.html?verify={expected}")
        require(f'"mainPack":"{pack}"' in html, f"public {game}: old pack config")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", action="store_true")
    args = parser.parse_args()
    try:
        current_version = local_check()
        if args.public:
            public_check(current_version)
        print(f"PASS CG entrances: {current_version}" + (" public" if args.public else " local"))
    except (RuntimeError, OSError, KeyError) as error:
        print(f"FAIL CG entrances: {error}", file=sys.stderr)
        sys.exit(1)
