#!/usr/bin/env bash
# Start only one listener per MIME family per user/session.
set -euo pipefail
for mime in text image; do
    if ! pgrep -u "$(id -u)" -fx "wl-paste --type $mime --watch cliphist store" >/dev/null; then
        wl-paste --type "$mime" --watch cliphist store >/dev/null 2>&1 &
    fi
done
