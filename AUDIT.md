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


## Automated validation

The repository now includes a GitHub Actions workflow that checks Waybar JSON, Starship TOML, selected INI files, Hyprland Lua syntax and archived shell helper syntax. A successful run confirms syntax only; it does not prove runtime compatibility on another machine.

## Repository review — November 5, 2026

This follow-up preserves the archive audit above. The baseline was commit `d690101` on local branch `work`, with a clean index and working tree. Existing documentation and validation improvements (`447b19e`, `1fb6b3b`, `d690101`) were retained. Work was prepared as an uncommitted diff on `audit/momo-refinement`.

### Scope and limitations

The review inventoried all **835 tracked entries**, including **111 internal symlinks**, and inspected the desktop configuration, documentation, package inventories, archived scripts and third-party resources. User configuration is under `home/`, optional system configuration under `system/`, and inactive helpers under `extras/`; the existing organization needs no restructuring.

Validation ran on Debian with Python 3.12 and the installed Lua 5.4 library. Neither Arch packages nor a Hyprland / SDDM desktop session were installed or started. Requests to GitHub and upstream documentation failed because the configured proxy was unreachable. Consequently, current upstream API support, package availability and the remote default branch could not be independently confirmed; local files are the evidence for this review.

### Findings and disposition

No critical issue or exposed credential was identified by the checks below. This is not a guarantee of security or license compliance.

| Priority | Evidence and impact | Action / remaining work |
| :--- | :--- | :--- |
| High — compatibility not established | `home/.config/hypr/hyprland.lua` uses `hl.*`; Waybar uses `ext/workspaces` and Lua `hyprctl dispatch` expressions. The snapshot records no tested versions. Valid Lua / JSON alone cannot establish runtime support. | Installation and README now state the prerequisite explicitly. Record known-good versions and verify the APIs in a real session before claiming reproducibility. No configuration conversion was attempted. |
| High — redistribution uncertainty | `home/.config/cava/shaders/eye_of_phi.frag` names a Shadertoy author without redistribution terms. Four `orion_*.frag` files have MIT SPDX headers but no accompanying MIT text for that author; the shader collection has no captured upstream release / license bundle. Screenshots contain third-party wallpaper artwork. | Preserve the files and notices; obtain authoritative provenance and applicable terms before claiming complete distribution compliance. Excluding original wallpaper files does not establish permission for artwork visible in screenshots. No license terms were assigned or assets removed. |
| Medium — incomplete optional GTK theme | `home/.local/share/themes/Dracula-pink-accent/gtk-3.0/gtk-widgets-assets.css` references three missing SVG assets; each `gtk-3.20/gtk*.css` and `gtk-4.0/gtk*.css` has fifteen distinct missing image targets. Examples include `../assets/checkbox-checked@2.svg` and `../assets/selection-mode-checkbox-unchecked.png`. | Documented the incomplete archive in the installation and asset notes. Materia remains the selected theme. Asset substitution could alter appearance and was not attempted. |
| Medium — dependency documentation | The launcher requests Iosevka Nerd Font, GTK requests Adwaita Sans Heavy, Waybar calls `pactl`, and Thunar calls `exo-open`. The practical installation command did not name their packages; optional SDDM QML imports also need Qt Quick and Qt 5 compatibility modules. | Added `ttf-iosevka-nerd`, `adwaita-fonts`, `libpulse` and `exo`, with the reason for each, and named optional `qt6-declarative` / `qt6-5compat` dependencies. Package inventories remain informational and unchanged. |
| Medium — incomplete installation recovery | Previous steps assumed `~/.config` and SDDM directories existed, did not cover replacing an existing SDDM theme, and provided no rollback procedure. | Added destination creation, private backup instructions and selective recovery that moves failed configuration aside before restoring. Package installation now documents a full Arch upgrade. |
| Medium — archived helpers are not standalone | `extras/unreferenced-scripts/hypr/scripts/momo-power.sh` expects absent `~/.config/waybar/scripts/session-menu.sh`. `rofi/scripts/momo-rofi.sh` expects helpers installed under `~/.config/rofi/scripts/`; its calculator needs `rofi-calc`, and `desktops.sh` calls `jq`. | Kept as inactive reference material. They are not installed by the guide; do not activate the archive as a complete integration. |
| Low — missing Waypaper resource | `home/.config/waypaper/config.ini` references `keybindings.ini`, which is not bundled. Whether the installed Waypaper version supplies defaults is unverified. | Documented the missing resource; no invented keybindings or behavior changes. |
| Low — screenshot privacy | All three showcase screenshots show a private LAN address. `desktop-fastfetch.png` also shows a local username / hostname and system details. | Retained the original images, documented disclosure and left any redaction to the owner. No visible credentials or PNG metadata fields were identified. |
| Low — documentation and coverage | The vendored Dracula README referenced an absent screenshot; publishing guidance used a personal checkout path; CI did not parse the Wlogout layout or SDDM overrides. | Linked to upstream previews without adding an image, made the publishing flow branch-specific and review-based, and extended the existing CI job with standard-library parsers. |

### Configuration consistency

- The keybinding reference matches the inspected Lua declarations; no shortcut changes were needed.
- Active Rofi imports resolve. All 111 symlinks resolve within the checkout.
- Startup services appear once in the supplied Lua file. External user services and other session autostart sources were not captured and may affect duplication on the real machine.
- SwayNC starts with defaults; no custom SwayNC configuration is bundled. Kitty uses the account login shell, not a forced Fish command.
- Cliphist wipes history at each Hyprland start, then records text and images through two watchers. No active history-picker shortcut is supplied.
- SDDM metadata identifies theme version 1.12.0 and Qt 6; its local QML component references exist. Rendering, PAM integration and session selection remain untested.

### Security and licensing review

Pattern scans of **669 locally reachable Git-history blobs** found no private-key headers, recognized GitHub / AWS / Google / Slack token patterns or obvious credential assignments. No tracked browser profiles, authentication databases or conventional secret filenames were identified. This coverage is limited to the local Git object graph and the patterns used; deleted or unreachable remote history was not examined. If a credential is discovered later, revoke it first: removing a current file alone does not remove history exposure.

Absolute home paths in some theme SVG metadata belong to upstream asset authors; runtime configuration does not use those paths. Existing GPL texts, SDDM MIT notices and Notwaita attribution were preserved byte-for-byte. Their presence records notices, not independent proof of provenance. No project-wide license was added; permission to redistribute the original dotfiles remains unspecified. Existing `.gitignore` rules already cover common backups, archives and credentials, so no broader exclusions were added.

### Validation boundary

The existing CI job now also parses Wlogout's consecutive JSON objects, seven INI files (including SDDM overrides / metadata / selector) and two XML files. It still checks Hyprland Lua and the six archived shell scripts. These checks validate file structure and syntax; they do not execute desktop actions, render CSS / QML, validate shaders or demonstrate hardware compatibility. The highest-priority follow-up is a real-session compatibility check with recorded versions, followed by resolution of the asset licensing uncertainties above.

Local results for this review:

- Passed the workflow's Python block: Waybar JSON, Starship TOML, four Wlogout objects, seven INI files and two XML files. Empty / non-object Wlogout input and trailing garbage were rejected in temporary negative checks.
- Passed Lua syntax parsing through the installed Lua 5.4 `luaL_loadfilex` API without executing the configuration. The `luac5.4` executable was unavailable, so the exact CI command was not run locally.
- Passed `bash -n` for all six archived helpers and the documented Bash blocks; the workflow YAML parsed successfully.
- Passed backup, selective copy and rollback exercises in temporary home directories, including an initially absent `~/.config`, retention of the failed copy and copying cursor symlinks. Privileged SDDM commands and Arch package transactions were reviewed but not executed.
- Resolved all local Markdown / HTML file and anchor references across 12 Markdown files. Verified all three showcase PNGs are readable and byte-identical to the baseline.
- Passed `git diff --check`. All changes are documentation or the existing validation workflow; active configuration, third-party code, licenses and binary assets remain unchanged. GitHub Actions itself was not run from this environment.
