#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${SCRIPT_DIR}/skills"

CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-${HOME}/.claude/skills}"
CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-${CODEX_HOME:-${HOME}/.codex}/skills}"

usage() {
  cat <<'EOF'
Usage: ./uninstall.sh [--claude-only | --codex-only]

Remove the symbolic links created by ./install.sh for every skill in ./skills.
Only links that point into this repository are removed; anything else (real
directories, links to other locations) is left untouched.

Environment variables:
  CLAUDE_SKILLS_DIR  Override Claude's skills directory
  CODEX_SKILLS_DIR   Override Codex's skills directory
  CODEX_HOME         Override Codex's home (used when CODEX_SKILLS_DIR is unset)
EOF
}

uninstall_claude=true
uninstall_codex=true

case "${1:-}" in
  "") ;;
  --claude-only) uninstall_codex=false ;;
  --codex-only) uninstall_claude=false ;;
  -h|--help) usage; exit 0 ;;
  *)
    echo "Unknown option: $1" >&2
    usage >&2
    exit 2
    ;;
esac

if [[ $# -gt 1 ]]; then
  echo "Only one option may be specified." >&2
  usage >&2
  exit 2
fi

if [[ ! -d "${SKILLS_DIR}" ]]; then
  echo "Skills directory not found: ${SKILLS_DIR}" >&2
  exit 1
fi

uninstall_skill() {
  local source=$1
  local destination_root=$2
  local platform=$3
  local name destination current_target

  name="$(basename -- "${source}")"
  destination="${destination_root}/${name}"

  if [[ ! -L "${destination}" ]]; then
    if [[ -e "${destination}" ]]; then
      echo "Skipped ${platform}/${name}: ${destination} is not a symlink" >&2
    else
      echo "Not installed for ${platform}: ${name}"
    fi
    return
  fi

  current_target="$(readlink -f -- "${destination}" 2>/dev/null || true)"
  if [[ "${current_target}" != "${source}" ]]; then
    echo "Skipped ${platform}/${name}: ${destination} links elsewhere" >&2
    return
  fi

  rm -- "${destination}"
  echo "Uninstalled for ${platform}: ${name}"
}

skill_count=0
while IFS= read -r -d '' skill_file; do
  skill_dir="$(dirname -- "${skill_file}")"
  ((skill_count += 1))

  if [[ "${uninstall_claude}" == true ]]; then
    uninstall_skill "${skill_dir}" "${CLAUDE_SKILLS_DIR}" "Claude"
  fi
  if [[ "${uninstall_codex}" == true ]]; then
    uninstall_skill "${skill_dir}" "${CODEX_SKILLS_DIR}" "Codex"
  fi
done < <(find "${SKILLS_DIR}" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -print0 | sort -z)

if (( skill_count == 0 )); then
  echo "No skills found in ${SKILLS_DIR}." >&2
  exit 1
fi
