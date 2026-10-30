#!/bin/sh
# PostToolUse: format and auto-fix a Python file Claude just edited (VS Code's format-on-save doesn't see Claude's edits).
file=$(jq -r '.tool_input.file_path // empty')
case "$file" in *.py) ;; *) exit 0 ;; esac
[ -f "$file" ] || exit 0
ruff="$CLAUDE_PROJECT_DIR/.venv/bin/ruff"
[ -x "$ruff" ] || ruff=$(command -v ruff) || exit 0  # no ruff yet (run make install); pre-commit still catches it
"$ruff" format --quiet "$file"
"$ruff" check --fix --quiet "$file" >&2 || true  # remaining lint errors go to Claude as feedback, never block
