#!/usr/bin/env bash
# Sets up this machine from the repo: symlinks every file in dotfiles/ into place, then installs the
# pstack and zstack plugins from the zzzint marketplace. Safe to run again.
#
#   ./link.sh          link and install
#   ./link.sh --check  report links that are missing or were replaced by a plain file; change nothing
#
# ZZZINT_SOURCE overrides where the marketplace is added from (default: the GitHub repo zzzint/config).
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
check=false
[[ "${1:-}" == "--check" ]] && check=true

# Each pair is a file in dotfiles/ and the path the app reads it from.
links=(
  "omp/AGENTS.md" "$HOME/.omp/agent/AGENTS.md"
  "omp/config.yml" "$HOME/.omp/agent/config.yml"
  "omp/mcp.json" "$HOME/.omp/agent/mcp.json"
  "tern/settings.json" "$HOME/Library/Application Support/Tern/settings.json"
  "zed/keymap.json" "$HOME/.config/zed/keymap.json"
)

drift=0
for ((i = 0; i < ${#links[@]}; i += 2)); do
  source="$repo/dotfiles/${links[i]}"
  target="${links[i + 1]}"

  if [[ -L "$target" && "$(readlink "$target")" == "$source" ]]; then
    echo "ok      $target"
    continue
  fi

  if $check; then
    if [[ -e "$target" ]]; then echo "drifted $target is not a link to $source"; else echo "missing $target"; fi
    drift=1
    continue
  fi

  mkdir -p "$(dirname "$target")"
  if [[ -e "$target" || -L "$target" ]]; then
    backup="$target.bak-$(date +%Y%m%d%H%M%S)"
    mv "$target" "$backup"
    echo "backup  $backup"
  fi
  ln -s "$source" "$target"
  echo "linked  $target"
done

if $check; then exit "$drift"; fi

if ! command -v omp >/dev/null; then
  echo "omp is not on PATH; install it, then run this again to add the plugins." >&2
  exit 1
fi

if ! omp plugin marketplace list | grep -Eq '^[[:space:]]+zzzint[[:space:]]'; then
  omp plugin marketplace add "${ZZZINT_SOURCE:-zzzint/config}"
fi

installed="$(omp plugin list --json)"
for plugin in pstack zstack; do
  if grep -q "\"id\": \"$plugin@zzzint\"" <<<"$installed"; then
    echo "ok      $plugin@zzzint"
  else
    omp plugin install "$plugin@zzzint"
  fi
done
