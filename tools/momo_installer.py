#!/usr/bin/env python3
"""MOMO installer: standard-library file handling and a native dialog UI.

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
DIALOG_THEME = ROOT / "assets" / "dialog" / "momo.dialogrc"

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
    if not DIALOG_THEME.is_file():
        raise InstallerError("Missing installer theme: assets/dialog/momo.dialogrc")
    for key, (_, paths) in COMPONENTS.items():
        for source, _ in paths:
            if not (ROOT / source).exists():
                raise InstallerError(f"Missing source for {key}: {source}")
    if not entries:
        raise InstallerError("Empty wallpaper catalog")
    return entries


def run_dialog(*args: str) -> str | None:
    if not DIALOG_THEME.is_file():
        raise InstallerError("Installer dialog theme is missing")
    command = ["dialog", "--stdout", "--clear", "--colors", "--no-shadow",
               "--cr-wrap", "--visit-items", "--backtitle",
               "MOMO   /   Arch Linux + Hyprland", *args]
    # DIALOGRC is scoped to this process; the user's ~/.dialogrc is untouched.
    env = {**os.environ, "DIALOGRC": str(DIALOG_THEME)}
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=False, env=env)
    if result.returncode in (1, 255):
        return None
    if result.returncode != 0:
        raise InstallerError(f"dialog failed with exit code {result.returncode}")
    return result.stdout.strip()


def select_options(catalog: list[dict]) -> tuple[list[str], list[dict]] | None:
    welcome = ("\\ZbMOMO DOTFILES\\Zn\n\n"
               "Select only the components you want. Your existing settings are "
               "moved into a private backup before any replacement.\n\n"
               "No packages are installed; the live desktop is not reloaded. "
               "System-wide SDDM setup remains manual.")
    if run_dialog("--title", "Welcome", "--msgbox", welcome, "13", "78") is None:
        return None

    menu = ["--title", "Desktop components", "--separate-output", "--checklist",
            "Space: toggle    |    Enter: continue    |    Esc: cancel",
            "21", "82", "13"]
    for key, (label, _) in COMPONENTS.items():
        menu += [key, label, "off"]
    menu += ["wallpapers", f"Wallhaven collection ({len(catalog)} files)", "off"]
    selected = run_dialog(*menu)
    if selected is None:
        return None
    keys = selected.splitlines() if selected else []
    unknown = set(keys) - set(COMPONENTS) - {"wallpapers"}
    if unknown:
        raise InstallerError(f"Unexpected component selections: {unknown}")

    wallpaper_items = []
    if "wallpapers" in keys:
        mode = run_dialog("--title", "Wallpapers", "--menu",
                          "Select how to import wallpapers into ~/Pictures (used by Waypaper).",
                          "14", "85", "4",
                          "all", f"Download all {len(catalog)} original files",
                          "choose", "Choose individual wallpapers",
                          "skip", "Do not download wallpapers")
        if mode is None:
            return None
        if mode == "all":
            wallpaper_items = catalog
        elif mode == "choose":
            choices = ["--title", "Choose wallpapers", "--separate-output", "--checklist",
                       "Choose by Wallhaven ID / dimensions. Original artwork is not bundled.",
                       "21", "85", "13"]
            for item in catalog:
                choices += [item["id"],
                            f'{item["width"]}x{item["height"]}  {item["bytes"] // 1048576} MiB  {item["filename"].split(".")[-1]}',
                            "off"]
            picked = run_dialog(*choices)
            if picked is None:
                return None
            picked_ids = set(picked.splitlines()) if picked else set()
            wallpaper_items = [w for w in catalog if w["id"] in picked_ids]
            if len(wallpaper_items) != len(picked_ids):
                raise InstallerError("Unexpected wallpaper selection")
        elif mode != "skip":
            raise InstallerError("Unexpected wallpaper download mode")
    keys = [key for key in keys if key != "wallpapers"]
    if not keys and not wallpaper_items:
        raise InstallerError("Nothing selected; no changes made")
    return keys, wallpaper_items


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
    if not keys:
        return None
    chosen = []
    for key in keys:
        if key not in COMPONENTS:
            raise InstallerError(f"Unknown component: {key}")
        chosen.extend(COMPONENTS[key][1])
    if len({dest for _, dest in chosen}) != len(chosen):
        raise InstallerError("Duplicate installation destinations")

    state = state_directory(home)
    reject_symlink_ancestors(state, stop=home)
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(state, 0o700)
    # Stage all copies before modifying even one destination.
    with tempfile.TemporaryDirectory(prefix="momo-stage-", dir=state) as stagedir:
        stage = Path(stagedir)
        for source, destination in chosen:
            src, dst = root / source, stage / destination
            if not src.exists():
                raise InstallerError(f"Missing source: {source}")
            validate_source_symlinks(src)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst, symlinks=True)
            else:
                shutil.copy2(src, dst, follow_symlinks=False)

        backup_parent = state / "backups"
        backup_parent.mkdir(exist_ok=True, mode=0o700)
        backup_root = Path(tempfile.mkdtemp(prefix="session-", dir=backup_parent))
        applied = []
        try:
            for _, relative in chosen:
                target = home / relative
                # Refuse traversing user-managed top-level config symlinks.
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
        try:
            msg = download_one(item, destination)
            successes += 1
            print(f"[{index}/{len(selected)}] {msg}", flush=True)
        except (InstallerError, OSError, ValueError, urllib.error.URLError) as err:
            failures += 1
            print(f"[{index}/{len(selected)}] FAILED {item['id']}: {err}", file=sys.stderr, flush=True)
        if index < len(selected) and interval:
            time.sleep(interval)  # Wallhaven documents an API request rate limit.
    return successes, failures


def main() -> int:
    parser = argparse.ArgumentParser(description="MOMO selective installer (no sudo or automatic packages)")
    parser.add_argument("--check", action="store_true", help="validate project files and wallpaper manifest without changing anything")
    parser.add_argument("--dry-run", action="store_true", help="choose options, then display the plan without changing anything")
    args = parser.parse_args()
    try:
        catalog = check_tree()
        if args.check:
            print(f"OK: {len(COMPONENTS)} components and {len(catalog)} wallpaper references")
            return 0
        if os.geteuid() == 0:
            raise InstallerError("Do not run MOMO with sudo or as root")
        if shutil.which("dialog") is None:
            raise InstallerError("Install the official Arch package first: sudo pacman -S --needed dialog")
        selected = select_options(catalog)
        if selected is None:
            print("Cancelled. No files changed.")
            return 0
        components, wallpaper_items = selected
        desc = "\\ZbSelected configuration groups:\\Zn\n" + ", ".join(components or ["none"])
        desc += f"\n\nWallpapers to download: {len(wallpaper_items)}"
        desc += "\nDestination: ~/Pictures (compatible with supplied Waypaper settings)"
        desc += "\n\nExisting selected configs are moved into a private timestamped backup."
        desc += "\nNo system-wide files or packages will be changed. Continue?"
        if run_dialog("--title", "Confirm changes", "--defaultno", "--yesno", desc, "17", "84") is None:
            print("Cancelled. No files changed.")
            return 0
        if args.dry_run:
            print("DRY RUN: no files changed, no network requests made.")
            print("Components:", ", ".join(components or ["none"]))
            print("Wallpapers:", ", ".join(w["id"] for w in wallpaper_items) or "none")
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
