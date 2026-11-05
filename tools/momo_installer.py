#!/usr/bin/env python3
"""MOMO installer: standard-library file handling and a Gum terminal UI.

No package manager calls, no sudo, no changes to a running Wayland session.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "wallpapers" / "catalog.json"

# Every entry is a repository-relative source and a home-relative destination.
# There is deliberately no automatic system-wide SDDM or package installation.
COMPONENTS = {
    "hyprland": ("Hyprland", (("home/.config/hypr", ".config/hypr"),)),
    "waybar": ("Waybar", (("home/.config/waybar", ".config/waybar"),)),
    "rofi": ("Rofi", (("home/.config/rofi", ".config/rofi"),)),
    "kitty": ("Kitty", (("home/.config/kitty", ".config/kitty"),)),
    "fish": ("Fish + Starship", (("home/.config/fish", ".config/fish"),
                                 ("home/.config/starship.toml", ".config/starship.toml"))),
    "waypaper": ("Waypaper", (("home/.config/waypaper", ".config/waypaper"),)),
    "wlogout": ("Wlogout", (("home/.config/wlogout", ".config/wlogout"),)),
    "thunar": ("Thunar", (("home/.config/Thunar", ".config/Thunar"),)),
    "gtk": ("GTK + nwg-look", (("home/.config/gtk-3.0", ".config/gtk-3.0"),
                                  ("home/.config/gtk-4.0", ".config/gtk-4.0"),
                                  ("home/.config/nwg-look", ".config/nwg-look"))),
    "cursor": ("Notwaita-Black", (("home/.local/share/icons/Notwaita-Black", ".local/share/icons/Notwaita-Black"),
                                   ("home/.local/share/icons/default", ".local/share/icons/default"))),
    "cava": ("Cava", (("home/.config/cava", ".config/cava"),)),
}
ID_PATTERN = re.compile(r"[a-z0-9]{6}\Z")
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
FILENAME_PATTERN = re.compile(r"wallhaven-([a-z0-9]{6})\.(jpg|png)\Z")


class InstallerError(Exception):
    """Expected error; can be displayed without a traceback."""


def load_catalog(path: Path = CATALOG) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise InstallerError("Unsupported wallpaper catalog version")
    items = data.get("wallpapers")
    if not isinstance(items, list):
        raise InstallerError("Catalog wallpapers must be a list")
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            raise InstallerError("Invalid catalog entry")
        wall_id = item.get("id")
        filename = item.get("filename")
        match = FILENAME_PATTERN.fullmatch(filename) if isinstance(filename, str) else None
        if not isinstance(wall_id, str) or not ID_PATTERN.fullmatch(wall_id) or not match or match.group(1) != wall_id:
            raise InstallerError(f"Invalid wallpaper ID or filename: {filename}")
        if wall_id in seen:
            raise InstallerError(f"Duplicate wallpaper ID: {wall_id}")
        seen.add(wall_id)
        if not isinstance(item.get("sha256"), str) or not HASH_PATTERN.fullmatch(item["sha256"]):
            raise InstallerError(f"Invalid checksum: {filename}")
        if any(type(item.get(field)) is not int or item[field] <= 0 for field in ("bytes", "width", "height")):
            raise InstallerError(f"Invalid dimensions or size: {filename}")
        if item.get("source") != f"https://wallhaven.cc/w/{wall_id}":
            raise InstallerError(f"Invalid source URL: {filename}")
    return items


def check_tree() -> list[dict]:
    entries = load_catalog()
    for key, (_, paths) in COMPONENTS.items():
        for source, _ in paths:
            if not (ROOT / source).exists():
                raise InstallerError(f"Missing source for {key}: {source}")
    if not entries:
        raise InstallerError("Empty wallpaper catalog")
    return entries


# Gum's documented CLI provides the display layer; it is never used for file writes.
# All choices use fixed IDs returned through --label-delimiter, never shell evaluation.
GUM_ENV = {
    "GUM_CHOOSE_CURSOR_FOREGROUND": "#50D6D8",
    "GUM_CHOOSE_HEADER_FOREGROUND": "#50D6D8",
    "GUM_CHOOSE_SELECTED_FOREGROUND": "#50D6D8",
    "GUM_CONFIRM_SELECTED_FOREGROUND": "#50D6D8",
}
PROFILES = {
    "minimal": ["hyprland", "waybar", "rofi", "kitty"],
    "complete": list(COMPONENTS),
}


def run_gum(*args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, **GUM_ENV}
    try:
        return subprocess.run(["gum", *args], stdout=subprocess.PIPE,
                              text=True, check=False, env=env)
    except FileNotFoundError as exc:
        raise InstallerError("Gum is required: sudo pacman -S --needed gum") from exc


def show_heading(title: str, subtitle: str = "") -> None:
    result = run_gum("style", "--foreground", "#50D6D8", "--border", "rounded",
                     "--border-foreground", "#343C44", "--padding", "1 2",
                     f"MOMO / {title}\n{subtitle}".rstrip())
    if result.returncode:
        raise InstallerError("gum style failed")
    print(result.stdout, flush=True)


def gum_choose(header: str, choices: list[tuple[str, str]],
               multiple: bool = False, height: int = 12) -> list[str] | None:
    if not choices:
        return []
    options = [f"{label}::{key}" for key, label in choices]
    cmd = ["choose", "--label-delimiter", "::", "--header", header,
           "--height", str(min(height, len(choices)))]
    if multiple:
        cmd.append("--no-limit")
    result = run_gum(*cmd, *options)
    if result.returncode in (1, 130):
        return None
    if result.returncode:
        raise InstallerError(f"gum choose failed ({result.returncode})")
    chosen = result.stdout.splitlines()
    known = {key for key, _ in choices}
    if any(key not in known for key in chosen) or len(chosen) != len(set(chosen)):
        raise InstallerError("Unexpected selection returned by Gum")
    if not multiple and len(chosen) != 1:
        raise InstallerError("Expected a single menu selection")
    return chosen


def gum_confirm(prompt: str) -> bool:
    result = run_gum("confirm", "--default=false", "--affirmative", "Proceed",
                     "--negative", "Cancel", prompt)
    if result.returncode == 0:
        return True
    if result.returncode in (1, 130):
        return False
    raise InstallerError(f"gum confirm failed ({result.returncode})")


def select_options(catalog: list[dict]) -> tuple[list[str], list[dict]] | None:
    show_heading("INSTALLER", "Selective configuration · private backups · no sudo")
    profile = gum_choose("01 / Choose installation profile", [
        ("minimal", "Minimal      · Hyprland, Waybar, Rofi, Kitty"),
        ("complete", "Complete     · All 11 component groups"),
        ("custom", "Custom       · Choose individual components"),
    ], height=3)
    if profile is None:
        return None
    if profile[0] == "custom":
        selection = gum_choose("02 / Space to select · Enter to continue", [
            (key, label) for key, (label, _) in COMPONENTS.items()
        ], multiple=True, height=11)
        if selection is None:
            return None
        keys = [key for key in COMPONENTS if key in selection]
    else:
        keys = PROFILES[profile[0]].copy()

    mode = gum_choose("03 / Wallpaper collection (optional)", [
        ("skip", "Skip wallpaper downloads"),
        ("all", f"Download all {len(catalog)} originals · verified SHA-256"),
        ("choose", "Pick individual wallpapers by Wallhaven ID"),
    ], height=3)
    if mode is None:
        return None
    wallpaper_items = []
    if mode[0] == "all":
        wallpaper_items = catalog
    elif mode[0] == "choose":
        picked = gum_choose("Space to select · Enter to continue", [
            (item["id"], f'{item["id"]}  {item["width"]}×{item["height"]}  '
                         f'{item["bytes"] / 1048576:.1f} MiB  {item["filename"].split(".")[-1].upper()}')
            for item in catalog
        ], multiple=True, height=14)
        if picked is None:
            return None
        ids = set(picked)
        wallpaper_items = [item for item in catalog if item["id"] in ids]
    if not keys and not wallpaper_items:
        raise InstallerError("Nothing selected; no changes made")
    return keys, wallpaper_items


def component_requirements(keys: list[str]) -> list[tuple[str, bool]]:
    commands = {
        "hyprland": ("Hyprland",), "waybar": ("waybar",),
        "rofi": ("rofi",), "kitty": ("kitty",),
        "fish": ("fish", "starship"), "waypaper": ("waypaper",),
        "wlogout": ("wlogout",), "thunar": ("thunar",),
        "gtk": ("nwg-look",), "cursor": (), "cava": ("cava",),
    }
    return [(exe, shutil.which(exe) is not None) for key in keys for exe in commands[key]]


def print_preflight(keys: list[str]) -> None:
    missing = [exe for exe, present in component_requirements(keys) if not present]
    if missing:
        print("\nMissing optional application commands:", ", ".join(sorted(set(missing))))
        print("MOMO installs configuration files only; use the official Arch packages as appropriate.")
    if "hyprland" in keys:
        print("Compatibility: workspace rules target DP-1; check Hyprland Lua API and your monitor.")
    if "waybar" in keys:
        print("Compatibility: NVIDIA/coretemp modules and ext/workspaces may need adjustments.")


def same_tree(source: Path, target: Path) -> bool:
    """Compare bytes, file modes and relative symlink values without following links."""
    if source.is_symlink() or target.is_symlink():
        return source.is_symlink() and target.is_symlink() and os.readlink(source) == os.readlink(target)
    if source.is_dir() != target.is_dir() or source.is_file() != target.is_file():
        return False
    if not target.exists():
        return False
    if source.is_dir():
        if source.stat().st_mode & 0o777 != target.stat().st_mode & 0o777:
            return False
        src_names = {p.name for p in source.iterdir()}
        if src_names != {p.name for p in target.iterdir()}:
            return False
        return all(same_tree(source / name, target / name) for name in src_names)
    if source.is_file():
        if source.stat().st_size != target.stat().st_size:
            return False
        if source.stat().st_mode & 0o777 != target.stat().st_mode & 0o777:
            return False
        with source.open("rb") as a, target.open("rb") as b:
            while True:
                left, right = a.read(1048576), b.read(1048576)
                if left != right:
                    return False
                if not left:
                    return True
    return False


def selected_paths(keys: list[str]) -> list[tuple[str, str]]:
    chosen = []
    for key in keys:
        if key not in COMPONENTS:
            raise InstallerError(f"Unknown component: {key}")
        chosen.extend(COMPONENTS[key][1])
    if len({dest for _, dest in chosen}) != len(chosen):
        raise InstallerError("Duplicate installation destinations")
    return chosen


def build_plan(keys: list[str], home: Path, root: Path = ROOT) -> list[tuple[str, str]]:
    entries = []
    for source, relative in selected_paths(keys):
        src, target = root / source, home / relative
        if not src.exists():
            raise InstallerError(f"Missing source: {source}")
        validate_source_symlinks(src)
        reject_symlink_ancestors(target.parent, stop=home)
        status = ("UNCHANGED" if same_tree(src, target) else
                  "REPLACE" if target.exists() or target.is_symlink() else "ADD")
        entries.append((relative, status))
    return entries


def print_plan(keys: list[str], wallpapers: list[dict], home: Path) -> None:
    print("\n04 / REVIEW FILE CHANGES")
    plan = build_plan(keys, home)
    for relative, status in plan:
        print(f"  {status:<9} {relative}")
    if not plan:
        print("  No configuration changes selected")
    size_mib = sum(w["bytes"] for w in wallpapers) / 1048576
    print(f"\nWallpaper originals selected: {len(wallpapers)} (~{size_mib:.0f} MiB; destination: ~/Pictures)")
    print_preflight(keys)
    if any(status == "REPLACE" for _, status in plan):
        print("Existing components will be moved into a private backup before replacement.")
    print("No package installation, sudo, SDDM changes or desktop reloads are performed.\n")



def state_directory(home: Path) -> Path:
    configured = os.environ.get("XDG_STATE_HOME")
    if configured:
        p = Path(configured)
        if p.is_absolute():
            return p / "momo"
    return home / ".local/state/momo"


def reject_symlink_ancestors(path: Path, stop: Path | None = None) -> None:
    """Refuse writing through symlinked directories, even if they already exist."""
    current = path
    while True:
        if current.is_symlink():
            raise InstallerError(f"Refusing symlinked directory: {current}")
        if current == current.parent or current == stop:
            break
        current = current.parent


def validate_source_symlinks(path: Path) -> None:
    """Ensure links shipped by the repository cannot escape their component."""
    if path.is_symlink():
        raise InstallerError(f"Top-level component is a symlink: {path}")
    if not path.is_dir():
        return
    root = path.resolve()
    for directory, dirs, files in os.walk(path, followlinks=False):
        for name in [*dirs, *files]:
            entry = Path(directory) / name
            if entry.is_symlink():
                target = (entry.parent / os.readlink(entry)).resolve(strict=False)
                if not target.is_relative_to(root):
                    raise InstallerError(f"Component contains an escaping symlink: {entry}")


def atomic_write_json(path: Path, obj: dict) -> None:
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def install_components(keys: list[str], home: Path, root: Path = ROOT) -> Path | None:
    chosen = selected_paths(keys)
    if not chosen:
        return None
    plan = build_plan(keys, home, root)
    operations = [pair for pair, (_, status) in zip(chosen, plan) if status != "UNCHANGED"]
    if not operations:
        print("All selected configurations are already identical; nothing replaced.")
        return None

    state = state_directory(home)
    reject_symlink_ancestors(state, stop=home)
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(state, 0o700)
    with tempfile.TemporaryDirectory(prefix="momo-stage-", dir=state) as stagedir:
        stage = Path(stagedir)
        for source, destination in operations:
            src, dst = root / source, stage / destination
            validate_source_symlinks(src)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst, symlinks=True)
            else:
                shutil.copy2(src, dst, follow_symlinks=False)

        backup_parent = state / "backups"
        reject_symlink_ancestors(backup_parent, stop=home)
        backup_parent.mkdir(exist_ok=True, mode=0o700)
        backup_root = Path(tempfile.mkdtemp(prefix="session-", dir=backup_parent))
        applied = []
        try:
            for _, relative in operations:
                target = home / relative
                reject_symlink_ancestors(target.parent, stop=home)
                target.parent.mkdir(parents=True, exist_ok=True)
                backup = backup_root / relative
                had_previous = target.exists() or target.is_symlink()
                entry = {"target": target, "backup": backup, "had_previous": had_previous,
                         "moved_previous": False, "installed": False}
                applied.append(entry)
                if had_previous:
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    target.rename(backup)
                    entry["moved_previous"] = True
                (stage / relative).rename(target)
                entry["installed"] = True
                print(f"Installed: {relative}", flush=True)
            records = [{"destination": str(e["target"].relative_to(home)),
                        "previous_version": e["had_previous"]} for e in applied]
            atomic_write_json(backup_root / "install-record.json", {"version": 1, "files": records})
            print(f"Original settings backed up to: {backup_root}")
            return backup_root
        except Exception:
            print("Installation interrupted; restoring original settings...", file=sys.stderr)
            for entry in reversed(applied):
                target, backup = entry["target"], entry["backup"]
                try:
                    if entry["installed"]:
                        quarantine = backup_root / "incomplete-install" / target.relative_to(home)
                        quarantine.parent.mkdir(parents=True, exist_ok=True)
                        target.rename(quarantine)
                    if entry["moved_previous"]:
                        backup.rename(target)
                except OSError as restore_error:
                    print(f"Manual recovery required for {target}: {restore_error}", file=sys.stderr)
            raise


def list_sessions(home: Path) -> list[Path]:
    backups = state_directory(home) / "backups"
    reject_symlink_ancestors(backups, stop=home)
    if not backups.is_dir():
        return []
    return sorted((p for p in backups.iterdir() if p.is_dir() and not p.is_symlink()
                   and p.name.startswith("session-") and (p / "install-record.json").is_file()),
                  key=lambda p: p.stat().st_mtime, reverse=True)


def read_session(session: Path, home: Path) -> list[tuple[str, bool]]:
    if session.is_symlink() or not session.is_dir() or not session.name.startswith("session-"):
        raise InstallerError("Invalid backup session")
    allowed = {dest for _, dest in selected_paths(list(COMPONENTS))}
    raw = json.loads((session / "install-record.json").read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("version") != 1 or not isinstance(raw.get("files"), list):
        raise InstallerError("Unsupported backup manifest")
    result = []
    for entry in raw["files"]:
        if (not isinstance(entry, dict) or entry.get("destination") not in allowed
                or type(entry.get("previous_version")) is not bool):
            raise InstallerError("Invalid backup manifest entry")
        relative, was_present = entry["destination"], entry["previous_version"]
        if relative in {r for r, _ in result}:
            raise InstallerError("Duplicate backup destination")
        old = session / relative
        if was_present and not (old.exists() or old.is_symlink()):
            raise InstallerError(f"Missing original in backup: {relative}")
        reject_symlink_ancestors((home / relative).parent, stop=home)
        result.append((relative, was_present))
    if not result:
        raise InstallerError("Empty backup manifest")
    return result


def restore_session(session: Path, home: Path) -> Path:
    """Restore a recorded install; keep both the saved originals and current files."""
    saved = read_session(session, home)
    state = state_directory(home)
    reject_symlink_ancestors(state, stop=home)
    restore_parent = state / "backups"
    reject_symlink_ancestors(restore_parent, stop=home)
    with tempfile.TemporaryDirectory(prefix="momo-restore-stage-", dir=state) as tmp:
        stage = Path(tmp)
        for relative, was_present in saved:
            if not was_present:
                continue
            source, copy = session / relative, stage / relative
            copy.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir() and not source.is_symlink():
                shutil.copytree(source, copy, symlinks=True)
            else:
                shutil.copy2(source, copy, follow_symlinks=False)
        restore_root = Path(tempfile.mkdtemp(prefix="restore-", dir=restore_parent))
        applied = []
        try:
            for relative, was_present in saved:
                target = home / relative
                reject_symlink_ancestors(target.parent, stop=home)
                target.parent.mkdir(parents=True, exist_ok=True)
                current = restore_root / relative
                had_current = target.exists() or target.is_symlink()
                entry = {"target": target, "current": current,
                         "moved_current": False, "restored": False}
                applied.append(entry)
                if had_current:
                    current.parent.mkdir(parents=True, exist_ok=True)
                    target.rename(current)
                    entry["moved_current"] = True
                if was_present:
                    (stage / relative).rename(target)
                    entry["restored"] = True
            atomic_write_json(restore_root / "restore-record.json", {
                "version": 1, "source": session.name,
                "files": [{"destination": r, "previous_version": present} for r, present in saved]
            })
            print(f"Restored {len(saved)} entries from {session.name}.")
            print(f"Pre-restore settings preserved at: {restore_root}")
            return restore_root
        except Exception:
            for entry in reversed(applied):
                try:
                    if entry["restored"]:
                        entry["target"].rename(stage / entry["target"].relative_to(home))
                    if entry["moved_current"]:
                        entry["current"].rename(entry["target"])
                except OSError as exc:
                    print(f"Manual restore required for {entry['target']}: {exc}", file=sys.stderr)
            raise



def allowed_image_url(value: str, wall_id: str, filename: str) -> bool:
    try:
        url = urllib.parse.urlsplit(value)
    except ValueError:
        return False
    # Wallhaven's official API returns URLs on its image host.
    return (url.scheme == "https" and url.hostname == "w.wallhaven.cc"
            and url.port in (None, 443) and not url.username and not url.password
            and not url.query and not url.fragment
            and url.path == f"/full/{wall_id[:2]}/{filename}")


def verified_existing(path: Path, item: dict) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    if path.stat().st_size != item["bytes"]:
        return False
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest() == item["sha256"]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise InstallerError(f"Refusing HTTP redirect for {request.full_url}")


def safe_urlopen(request: urllib.request.Request, timeout: int):
    """Never follow HTTP redirects, including HTTPS-to-HTTP downgrades."""
    return urllib.request.build_opener(_NoRedirect()).open(request, timeout=timeout)


def _request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "MOMO-Dotfiles/1.0 (+https://github.com/vampr5861-debug/arch-hyprland-dotfiles)",
                                                   "Accept": "application/json"})
    with safe_urlopen(req, timeout=25) as response:
        # Do not follow an API redirect to HTTP, another host or another path.
        if response.geturl() != url:
            raise InstallerError("Wallpaper API redirected unexpectedly")
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise InstallerError("Wallpaper metadata response is too large")
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as exc:
            raise InstallerError("Wallpaper API returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise InstallerError("Wallpaper API returned an invalid JSON object")
        return data


def download_one(item: dict, target_dir: Path) -> str:
    path = target_dir / item["filename"]
    if path.exists() or path.is_symlink():
        if verified_existing(path, item):
            return f"Already downloaded: {item['filename']}"
        raise InstallerError(f"Existing file differs; refusing to overwrite: {path}")
    data = _request_json(f"https://wallhaven.cc/api/v1/w/{item['id']}").get("data", {})
    if not isinstance(data, dict) or data.get("id") != item["id"]:
        raise InstallerError(f"Unexpected API result for {item['id']}")
    if data.get("purity") != "sfw":
        raise InstallerError(f"Wallpaper unavailable for guest/SFW download: {item['id']}")
    url = data.get("path")
    if not isinstance(url, str) or not allowed_image_url(url, item["id"], item["filename"]):
        raise InstallerError(f"Unexpected image URL for {item['id']}")

    temp_name = None
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "MOMO-Dotfiles/1.0"})
        with safe_urlopen(request, timeout=60) as response:
            if response.geturl() != url:
                raise InstallerError("Image download redirected unexpectedly")
            media = (response.headers.get("Content-Type") or "").split(";", 1)[0].lower()
            expected_media = "image/png" if item["filename"].endswith(".png") else "image/jpeg"
            if media != expected_media:
                raise InstallerError(f"Unexpected content type for {item['id']}: {media}")
            with tempfile.NamedTemporaryFile(mode="wb", dir=target_dir, prefix=".momo-", delete=False) as stream:
                temp_name = stream.name
                total = 0
                digest = hashlib.sha256()
                while True:
                    block = response.read(1048576)
                    if not block:
                        break
                    total += len(block)
                    if total > item["bytes"]:
                        raise InstallerError(f"Unexpected size for {item['id']}")
                    digest.update(block)
                    stream.write(block)
        if total != item["bytes"] or digest.hexdigest() != item["sha256"]:
            raise InstallerError(f"Original changed or download corrupted: {item['id']}")
        # An exclusive hardlink avoids overwriting any concurrently created target.
        os.link(temp_name, path)
        return f"Downloaded: {item['filename']}"
    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)


def download_wallpapers(selected: list[dict], home: Path, interval: float = 1.5) -> tuple[int, int]:
    if not selected:
        return 0, 0
    destination = home / "Pictures"
    reject_symlink_ancestors(destination, stop=home)
    destination.mkdir(parents=True, exist_ok=True)
    successes, failures = 0, 0
    print(f"Wallpapers destination: {destination}", flush=True)
    for index, item in enumerate(selected, 1):
        for attempt in range(3):
            try:
                msg = download_one(item, destination)
                successes += 1
                print(f"[{index}/{len(selected)}] {msg}", flush=True)
                break
            except urllib.error.HTTPError as err:
                # Only temporary API/server failures get a bounded retry.
                if attempt < 2 and err.code in (429, 500, 502, 503, 504):
                    print(f"[{index}/{len(selected)}] HTTP {err.code}; retrying...", flush=True)
                    time.sleep(3 * (attempt + 1))
                    continue
                failures += 1
                print(f"[{index}/{len(selected)}] FAILED {item['id']}: HTTP {err.code}",
                      file=sys.stderr, flush=True)
                break
            except urllib.error.URLError as err:
                if attempt < 2:
                    print(f"[{index}/{len(selected)}] Network error; retrying...", flush=True)
                    time.sleep(3 * (attempt + 1))
                    continue
                failures += 1
                print(f"[{index}/{len(selected)}] FAILED {item['id']}: {err}",
                      file=sys.stderr, flush=True)
                break
            except (InstallerError, OSError, ValueError) as err:
                failures += 1
                print(f"[{index}/{len(selected)}] FAILED {item['id']}: {err}",
                      file=sys.stderr, flush=True)
                break
        if index < len(selected) and interval:
            time.sleep(interval)  # Respect Wallhaven's documented API rate limit.
    return successes, failures



def main() -> int:
    parser = argparse.ArgumentParser(description="MOMO selective installer (Gum UI, no sudo or package installation)")
    parser.add_argument("--check", action="store_true", help="validate project files without changing anything")
    parser.add_argument("--dry-run", action="store_true", help="show selection and file plan without writing or downloading")
    parser.add_argument("--doctor", action="store_true", help="report which application commands are installed")
    parser.add_argument("--restore", action="store_true", help="interactively restore a previous MOMO session")
    args = parser.parse_args()
    try:
        catalog = check_tree()
        if args.check:
            print(f"OK: {len(COMPONENTS)} components and {len(catalog)} wallpaper references")
            return 0
        if args.doctor:
            print("MOMO application readiness (not a guarantee of runtime compatibility):")
            for command, installed in component_requirements(list(COMPONENTS)):
                print(f"  {'OK' if installed else 'MISSING':<8} {command}")
            print_preflight(["hyprland", "waybar"])
            return 0
        if os.geteuid() == 0:
            raise InstallerError("Do not run MOMO with sudo or as root")
        if shutil.which("gum") is None:
            raise InstallerError("Install official Arch package first: sudo pacman -S --needed gum")
        if args.restore:
            sessions = list_sessions(Path.home())
            if not sessions:
                raise InstallerError("No MOMO backup sessions available")
            show_heading("RESTORE", "Restore earlier settings, preserving current files")
            chosen = gum_choose("Choose backup session", [(p.name, p.name) for p in sessions], height=10)
            if chosen is None:
                print("Cancelled. No files changed.")
                return 0
            session = next(p for p in sessions if p.name == chosen[0])
            changes = read_session(session, Path.home())
            print("Restore plan:")
            for relative, was_present in changes:
                print(f"  {'RESTORE' if was_present else 'REMOVE':<9} {relative}")
            print("Current versions will be preserved in a new private backup.")
            if not gum_confirm("Restore selected backup?"):
                print("Cancelled. No files changed.")
                return 0
            restore_session(session, Path.home())
            return 0

        selected = select_options(catalog)
        if selected is None:
            print("Cancelled. No files changed.")
            return 0
        components, wallpaper_items = selected
        print_plan(components, wallpaper_items, Path.home())
        if args.dry_run:
            print("DRY RUN: no files changed, no network requests made.")
            return 0
        if not gum_confirm("Install selected MOMO components and wallpapers?"):
            print("Cancelled. No files changed.")
            return 0
        backup = install_components(components, Path.home())
        ok, failed = download_wallpapers(wallpaper_items, Path.home())
        print("\nMOMO setup finished.")
        if backup:
            print(f"Backup directory: {backup}")
        if wallpaper_items:
            print(f"Wallpapers: {ok} ready, {failed} unavailable or failed")
        print("Review hardware-specific settings before starting Hyprland. Read docs/INSTALLER.md.")
        return 1 if failed else 0
    except (InstallerError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"MOMO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
