#!/usr/bin/env bash
# MOMO: optional, selective desktop configuration installer.
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec python3 "$project_root/tools/momo_installer.py" "$@"
