# Keybindings

These shortcuts are transcribed from the repository's [Hyprland Lua configuration](../home/.config/hypr/hyprland.lua). They describe this snapshot, not generic Hyprland defaults.

- **Super** is the Windows / Meta key.
- **LMB / RMB** mean the left / right mouse button.
- Media shortcuts use the keyboard's dedicated media keys.

## Applications and desktop

| Shortcut | Action |
| :--- | :--- |
| <kbd>Super</kbd> + <kbd>Enter</kbd> | Open Kitty |
| <kbd>Super</kbd> + <kbd>E</kbd> | Open Thunar |
| <kbd>Super</kbd> + <kbd>B</kbd> | Open Firefox |
| <kbd>Super</kbd> + <kbd>Space</kbd> or <kbd>Super</kbd> + <kbd>R</kbd> | Open the Rofi application launcher |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>Space</kbd> | Open the Rofi window switcher |
| <kbd>Super</kbd> + <kbd>W</kbd> | Open Waypaper |
| <kbd>Super</kbd> + <kbd>S</kbd> | Toggle the SwayNC notification center |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>N</kbd> | Dismiss notifications |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>B</kbd> | Toggle Waybar visibility |
| <kbd>Super</kbd> + <kbd>L</kbd> | Lock the screen with Hyprlock |
| <kbd>Super</kbd> + <kbd>Esc</kbd> | Open Wlogout |
| <kbd>Print</kbd> | Copy an output screenshot to the clipboard |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd> | Copy a selected-region screenshot to the clipboard |
| <kbd>Alt</kbd> + <kbd>Shift</kbd> | Switch between US and Russian layouts |

## Window management

| Shortcut | Action |
| :--- | :--- |
| <kbd>Super</kbd> + <kbd>Q</kbd> | Close the focused window |
| <kbd>Super</kbd> + <kbd>Ctrl</kbd> + <kbd>Q</kbd> | Kill the focused window |
| <kbd>Super</kbd> + <kbd>V</kbd> | Toggle floating / tiled mode |
| <kbd>Super</kbd> + <kbd>F</kbd> | Toggle fullscreen |
| <kbd>Super</kbd> + <kbd>M</kbd> | Toggle maximized state |
| <kbd>Super</kbd> + <kbd>P</kbd> | Toggle pseudotiling |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> | Pin the floating window |
| <kbd>Super</kbd> + <kbd>Alt</kbd> + <kbd>C</kbd> | Center the floating window |
| <kbd>Super</kbd> + <kbd>← ↑ ↓ →</kbd> | Focus a window in that direction |
| <kbd>Super</kbd> + <kbd>Backspace</kbd> | Focus the previously focused window |
| <kbd>Super</kbd> + <kbd>Tab</kbd> or <kbd>Alt</kbd> + <kbd>Tab</kbd> | Cycle to the next window |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>← ↑ ↓ →</kbd> | Move the focused window |
| <kbd>Super</kbd> + <kbd>Ctrl</kbd> + <kbd>← ↑ ↓ →</kbd> | Resize the focused window |
| <kbd>Super</kbd> + <kbd>Alt</kbd> + <kbd>← ↑ ↓ →</kbd> | Swap with a window in that direction |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>T</kbd> | Swap the Dwindle split |
| <kbd>Super</kbd> + <kbd>[</kbd> / <kbd>]</kbd> | Adjust the Dwindle split ratio |
| <kbd>Super</kbd> + <kbd>left mouse button</kbd> | Drag / move a window |
| <kbd>Super</kbd> + <kbd>right mouse button</kbd> | Resize a window |

## Workspaces, scratchpad and groups

| Shortcut | Action |
| :--- | :--- |
| <kbd>Super</kbd> + <kbd>1–6</kbd> | Switch to workspace 1–6 |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>1–6</kbd> | Move the focused window to workspace 1–6 |
| <kbd>Super</kbd> + <kbd>mouse wheel</kbd> | Cycle workspaces |
| <kbd>Super</kbd> + <kbd>grave</kbd> | Show / hide the scratchpad |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>grave</kbd> | Move the focused window to the scratchpad |
| <kbd>Super</kbd> + <kbd>G</kbd> | Toggle window grouping |
| <kbd>Super</kbd> + <kbd>Ctrl</kbd> + <kbd>G</kbd> | Select the next window in a group |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd> | Select the previous window in a group |

A three-finger horizontal touchpad gesture switches workspaces.

## Audio and media keys

| Key | Action |
| :--- | :--- |
| <kbd>XF86AudioRaiseVolume</kbd> | Increase output volume by 5% |
| <kbd>XF86AudioLowerVolume</kbd> | Decrease output volume by 5% |
| <kbd>XF86AudioMute</kbd> | Toggle output mute |
| <kbd>XF86AudioMicMute</kbd> | Toggle microphone mute |
| <kbd>XF86AudioPlay</kbd> | Toggle playback |
| <kbd>XF86AudioPause</kbd> | Pause playback |
| <kbd>XF86AudioNext</kbd> | Next track |
| <kbd>XF86AudioPrev</kbd> | Previous track |

Media playback shortcuts call `playerctl`. Install it if those keys are unavailable.

## Wlogout keyboard controls

| Key | Action |
| :--- | :--- |
| <kbd>S</kbd> | Shut down |
| <kbd>R</kbd> | Reboot |
| <kbd>E</kbd> | Log out |
| <kbd>L</kbd> | Lock |

Wlogout's layout defines the action keys; arrow-key / Tab navigation depends on the GTK focus behavior of the installed Wlogout build.
