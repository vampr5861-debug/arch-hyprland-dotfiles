#!/usr/bin/env bash
# Four tabs for the usual Super+Space launcher, using the user's existing theme.
set -euo pipefail
scripts="$HOME/.config/rofi/scripts"
case "${1:-drun}" in
    drun|calc|clipboard|desktops) mode="${1:-drun}" ;;
    *) echo "Unknown Rofi mode" >&2; exit 2 ;;
esac
exec rofi -config "$HOME/.config/rofi/momo-launcher.rasi" -show "$mode" \
    -modi "drun,calc,clipboard:${scripts}/clipboard.sh,desktops:${scripts}/desktops.sh" \
    -calc-command "printf '%s' '{result}' | wl-copy"
