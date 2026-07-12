#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${SCRIPT_DIR}/skills"

CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-${HOME}/.claude/skills}"
CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-${CODEX_HOME:-${HOME}/.codex}/skills}"

usage() {
  cat <<'EOF'
Usage: ./install.sh [--claude-only | --codex-only]

Install every skill in ./skills for Claude Code and Codex. Skills are installed
as symbolic links, so changes made in this repository are available immediately.

Environment variables:
  CLAUDE_SKILLS_DIR  Override Claude's skills directory
  CODEX_SKILLS_DIR   Override Codex's skills directory
  CODEX_HOME         Override Codex's home (used when CODEX_SKILLS_DIR is unset)
EOF
}

install_claude=true
install_codex=true

case "${1:-}" in
  "") ;;
  --claude-only) install_codex=false ;;
  --codex-only) install_claude=false ;;
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

install_skill() {
  local source=$1
  local destination_root=$2
  local platform=$3
  local name destination current_target

  name="$(basename -- "${source}")"
  destination="${destination_root}/${name}"
  mkdir -p -- "${destination_root}"

  if [[ -L "${destination}" ]]; then
    current_target="$(readlink -f -- "${destination}" 2>/dev/null || true)"
    if [[ "${current_target}" == "${source}" ]]; then
      echo "Already installed for ${platform}: ${name}"
      return
    fi
    echo "Skipped ${platform}/${name}: ${destination} links elsewhere" >&2
    return
  fi

  if [[ -e "${destination}" ]]; then
    echo "Skipped ${platform}/${name}: ${destination} already exists" >&2
    return
  fi

  ln -s -- "${source}" "${destination}"
  echo "Installed for ${platform}: ${name} -> ${source}"
}

skill_count=0
while IFS= read -r -d '' skill_file; do
  skill_dir="$(dirname -- "${skill_file}")"
  ((skill_count += 1))

  if [[ "${install_claude}" == true ]]; then
    install_skill "${skill_dir}" "${CLAUDE_SKILLS_DIR}" "Claude"
  fi
  if [[ "${install_codex}" == true ]]; then
    install_skill "${skill_dir}" "${CODEX_SKILLS_DIR}" "Codex"
  fi
done < <(find "${SKILLS_DIR}" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -print0 | sort -z)

if (( skill_count == 0 )); then
  echo "No skills found in ${SKILLS_DIR}." >&2
  exit 1
fi
