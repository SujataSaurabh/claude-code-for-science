#!/usr/bin/env bash
# PostToolUse hook: ruff check (report-only) on .py edits.
# Fails open on parse error. On lint failure: writes combined output to stderr
# and exits 2 so Claude Code surfaces it to Claude.

INPUT=$(cat)

FILE_PATH=$(printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    sys.stderr.write('ruff-check: could not parse hook JSON, skipping\n')
")

if [[ -z "$FILE_PATH" || "$FILE_PATH" != *.py ]]; then
    exit 0
fi

OUTPUT=$(ruff check "$FILE_PATH" 2>&1)
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    printf '%s\n' "$OUTPUT" >&2
    exit 2
fi
