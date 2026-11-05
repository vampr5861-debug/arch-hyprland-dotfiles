# GTK Themes and Cursor Assets

The following local resources were copied from the supplied theme archive without conversion or installation into the author's running system:

- `home/.local/share/themes/Dracula-pink-accent/` — GTK theme. Its original `LICENSE` (GPL-3.0) and upstream `README.md` are preserved. Upstream: [Dracula GTK](https://github.com/dracula/gtk), maintained by Eliver Lara and contributors.
- `home/.local/share/icons/Notwaita-Black/` — cursor theme. See the [Notwaita licensing notice](../../LICENSES/notwaita-cursor-NOTICE.md).
- `home/.local/share/icons/default/index.theme` — default cursor selection.

**Important:** the exported `gtk-3.0/settings.ini`, `gtk-4.0/settings.ini` and `xsettingsd.conf` select `Materia-dark`, **not** `Dracula-pink-accent`. The latter is included as an option but is not verified to be the currently active GTK theme. Do not switch it automatically.

**Not included:** `Bibata-Modern-Ice`, the system-installed `Materia-dark` theme, `Papirus-Dark`, certain third-party fonts and Wallhaven wallpaper files. Install these separately from trusted sources where necessary.

The Notwaita archive contains relative symlinks that resolve within the included cursor directory. Preserve symlinks when copying the cursor on Linux.
