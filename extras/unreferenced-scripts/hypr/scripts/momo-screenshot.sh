
#!/usr/bin/env bash
set -euo pipefail

case "${1:-}" in
    region)
        geometry="$(slurp)" || exit 0
        grim -g "$geometry" - | wl-copy --type image/png
        ;;
    full)
        grim - | wl-copy --type image/png
        ;;
    *)
        echo "Usage: $0 {region|full}" >&2
        exit 2
        ;;
esac
