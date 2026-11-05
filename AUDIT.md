# Configuration Audit — November 5, 2026

This is a **static audit** of the supplied configuration archives, not a live test of a fresh Arch Linux installation. The original audit archive (`arch-dotfiles-audit.tar.gz`) contained 67 regular files across 22 directories (918,101 total bytes of regular-file content).

## What was found

1. **Hyprland:** Lua configuration with startup commands for Waybar, Waypaper, Hyprsunset, SwayNC, clipboard watchers and hyprpolkitagent.
2. **Rofi:** `style-8.rasi` is used for the application launcher (`Super + Space` and `Super + R`); `config.rasi` also applies to other Rofi invocations such as the window switcher.
3. **SDDM:** QML theme files, base theme settings and the customized `theme.conf.user` were captured. Unneeded example themes were left out.
4. **Wlogout:** the four original PNG icons had uncertain provenance and were excluded from the public copy.
5. **GTK:** exported settings select `Materia-dark`; the separately supplied `Dracula-pink-accent` theme is included but is not selected by those settings.

## Adjustments made to the exported copy

These changes were made **only in the published copy**, not in the running Arch installation:

- **Waybar:** a hardcoded `/home/dev/...` path was replaced with a home-relative reference.
- **Waybar:** Intel CPU temperature is referenced through the standard `coretemp` sensor name.
- **Wlogout:** icons of uncertain origin were removed; text labels were substituted and CSS icon references removed. Visual appearance on another machine has not been tested.
- **Waypaper:** the stylesheet path was made home-relative.

## Included resources

- `Dracula-pink-accent` and `Notwaita-Black` were added from the separately supplied `dotfiles-themes.tar.gz` archive, preserving 647 regular files and 111 internal relative symlinks.
- The GTK theme retains its upstream GPL-3.0 file and README.
- Notwaita attribution and license references are documented in [LICENSES/notwaita-cursor-NOTICE.md](LICENSES/notwaita-cursor-NOTICE.md).
- Explicitly installed package snapshots are provided: **129 official** and **11 foreign** packages. The foreign category does not necessarily mean AUR-only.
- Desktop, Waypaper and Rofi screenshots were supplied for the documentation.

## Not included / not fully verified

- Wallpaper files from `~/Pictures`, including `wallhaven-n6y9zl.jpg` (redistribution rights not confirmed).
- The local `Bibata-Modern-Ice` cursor, system `Materia-dark` theme, certain Nerd Fonts and other system-provided themes.
- A complete package inventory including transitive dependencies, version pinning and portability checks.
- Any additional configuration outside the supplied archives, including potential user services and application data.
- Original Wlogout PNG icons, excluded for licensing reasons.
- Compatibility and appearance on other GPUs, screen resolutions and Hyprland releases.

## Static security review

- No obvious PEM/OpenSSH private keys, GitHub personal access tokens or conventional API token patterns were found in the reviewed configuration files. **Pattern-based scanning is not a security guarantee.**
- Email addresses appearing in some Cava shader headers belong to upstream attribution, not the repository owner's account details.
- The repository is **publicly available**. Review future changes for secrets and personal information before every push.

## Other findings

- `momo-power.sh` references a missing `session-menu.sh`.
- Unreferenced helper scripts are preserved in `extras/unreferenced-scripts/` rather than installed as part of the active setup.
- Rofi files derived from `adi1090x/rofi` retain the corresponding GPL-3.0 license notice.
- Some screenshots visibly show a private LAN address (`192.168.x.x`); this is not an Internet-routable public address, but it may still be worth redacting for privacy.

**Scope:** this is a documentation and file-content audit, not an independent live installation test.
