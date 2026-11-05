# MOMO Installer

MOMO offers an **optional interactive installer** for an existing Arch Linux desktop. It is a Python 3 application with a terminal interface powered by [Gum](https://github.com/charmbracelet/gum), available from Arch's official `extra` repository. It uses standard file operations and the official Wallhaven API; it does not install packages, change your login shell, configure SDDM, or restart Hyprland.

> [!IMPORTANT]
> This is a personal configuration snapshot, **not a turnkey Arch Linux installation**. Read [Installation](INSTALLATION.md) and [Customization](CUSTOMIZATION.md) before using a configuration on another machine. In particular, verify the installed Hyprland Lua API, Waybar module support, monitor output names and hardware-specific sensors.

## Start

From a cloned repository, install the official terminal UI package **yourself**:

```bash
sudo pacman -S --needed gum
```

Python 3 is also required. MOMO uses Gum's documented `style`, `choose`, and `confirm` commands, with scoped color settings. The installer does not modify your terminal theme, login shell, or Gum configuration. Inspect the installer and the components you plan to use before proceeding:

```bash
bash install.sh --check
bash install.sh --doctor
bash install.sh --dry-run
bash install.sh
```

- `--check` validates the manifest and component source paths without starting Gum, changing files or accessing the network.
- `--doctor` lists the availability of the applications required by each component and highlights hardware-specific assumptions. It never installs packages.
- `--dry-run` opens the Gum interface, chooses a profile and wallpapers, then shows an **ADD / REPLACE / UNCHANGED** plan without writing files or downloading anything.
- The regular command lets you choose **Minimal** (Hyprland, Waybar, Rofi, Kitty), **Complete** (11 groups), or **Custom**, then **skip**, **download all**, or **choose individual** wallpapers.
- Use arrow keys to navigate, **Space** to select multiple items, **Enter** to continue and **Esc** to cancel. The final install confirmation defaults to **No**.
- The installer skips identical existing configurations; a re-run with unchanged source files creates no additional backup for those components.
- Run the installer as your **ordinary user, never with `sudo`**. A sufficient existing Arch setup and the listed applications are prerequisites. The installer does not use `pacman` or an AUR helper.

## What is installed

| Menu group | Target in your home directory |
| :--- | :--- |
| Hyprland | `.config/hypr/` (including Hyprlock and Hyprpaper settings) |
| Waybar | `.config/waybar/` |
| Rofi | `.config/rofi/` |
| Kitty | `.config/kitty/` |
| Fish + Starship | `.config/fish/`, `.config/starship.toml` |
| Waypaper | `.config/waypaper/` |
| Wlogout | `.config/wlogout/` |
| Thunar | `.config/Thunar/` |
| GTK + nwg-look | `.config/gtk-3.0/`, `.config/gtk-4.0/`, `.config/nwg-look/` |
| Notwaita-Black | `.local/share/icons/Notwaita-Black/`, `.local/share/icons/default/` |
| Cava | `.config/cava/` |

**Only selected groups are copied.** The installer checks for identical destinations, stages changed copies first, moves only changed previous destinations into a private backup, and places the new files at their destinations. It does not merge directory contents, follow an existing symlinked configuration parent or activate desktop services. Copying the Fish configuration does not change your login shell. The optional system-wide SDDM configuration must be installed manually using the instructions in [Installation](INSTALLATION.md).

### Backups and recovery

Backups are created under `$XDG_STATE_HOME/momo/backups/` (or `~/.local/state/momo/backups/` when `XDG_STATE_HOME` is unset). Each session has its own unique directory and an `install-record.json` describing exactly which home-relative destinations were updated. **Keep that directory** until you are satisfied with the new configuration. It can contain sensitive settings.

To restore a previously installed set of components, run:

```bash
bash install.sh --restore
```

Choose a recorded session and inspect the restore plan. The **RESTORE** action restores previous files; **REMOVE** means the selected path did not exist before that session. The restore operation preserves the current versions in a new private `restore-*` backup, **keeps the original backup session**, and requires explicit confirmation. This restores MOMO-managed configuration paths only, not the OS or the wallpaper downloads. It is still best-effort if the machine loses power during a file operation.

If a file operation fails during installation, the installer attempts to move all newly installed components aside and restore the originals. This is a best-effort rollback, not a substitute for a system backup. If the process is terminated abruptly (for example, by power loss), recover from the printed backup path.

To manually restore one component, first **move the newly installed directory aside** and then move the matching original directory from your saved backup back to its previous location. For example, with the actual backup path from your run:

```bash
backup_root="$HOME/.local/state/momo/backups/session-REPLACE_ME"
mv "$HOME/.config/waybar" "$HOME/.config/waybar.momo-new"
mv "$backup_root/.config/waybar" "$HOME/.config/waybar"
```

If you had no previous configuration for that component, simply move the newly installed one aside; no original will exist in the backup. **Do not run the example with the placeholder backup path unchanged.** A custom `$XDG_STATE_HOME` changes the backup location.

## Wallpapers

The [`wallpapers/catalog.json`](../wallpapers/catalog.json) file describes **79 Wallhaven IDs** extracted from a supplied personal collection, including dimensions, original file sizes and SHA-256 checksums. **No image files are included in this repository.** The catalog links to the original source pages at `wallhaven.cc/w/<ID>`.

The optional downloader uses Wallhaven's [documented wallpaper API](https://wallhaven.cc/help/api) to locate an image, then checks that the download uses Wallhaven's image host, is an SFW image available to guests, matches the expected file type, length, and SHA-256. Images that are removed, restricted or changed since the original snapshot are reported as unavailable rather than silently substituted. The original 79 IDs have **not** been individually checked for live download availability.

Wallpapers are downloaded into **`~/Pictures/`** with their original filenames. This matches the included Waypaper configuration, which reads from `~/Pictures` without descending into subfolders and initially points at `~/Pictures/wallhaven-n6y9zl.jpg`. Downloading wallpapers does **not** change the active wallpaper, run Waypaper, or modify its configuration. Existing files are never overwritten; identical files are skipped, and different files cause a warning. A failed or interrupted transfer leaves no partially installed wallpaper.

Wallhaven documents an API rate limit; downloading the whole collection may take a while. MOMO reports each file and retries a limited number of times on temporary network or server errors (such as HTTP 429 and 503); checksum mismatches are never automatically accepted. The 79 originals represented about 209 MB at the time of the supplied archive. **Do not assume every original remains available.** No API key is required for public SFW images, and the installer neither requests nor stores an API key.

> [!CAUTION]
> Wallhaven hosts user-submitted images; rights remain with the original creators. A link or a personal copy is not a redistribution license. Verify rights before publishing or reusing the artwork. Some original files contain EXIF metadata; avoid publishing them without a privacy review. This repository deliberately stores a **link-and-checksum catalog**, not the wallpaper binaries.

## Validation and scope

The standard-library unit tests and GitHub Actions checks cover catalog structure, URL validation, redirect refusal, Gum argument construction, planning, repeat installation, symlink checks, safe downloads, backups, restoration, and rollback logic. They do **not** perform live downloads or prove that the configuration works with every Hyprland/Waybar release, GPU, display or system. See [Troubleshooting](TROUBLESHOOTING.md) if any selected desktop component fails at runtime.
