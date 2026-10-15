#!/usr/bin/env bash
# PostToolUse hook: pytest on test_*.py edits only.
# Fails open on parse error. On test failure: writes combined output to stderr
# and exits 2 so Claude Code surfaces it to Claude.

INPUT=$(cat)

FILE_PATH=$(printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    sys.stderr.write('pytest-check: could not parse hook JSON, skipping\n')
")

if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

BASENAME=$(basename "$FILE_PATH")
if [[ "$BASENAME" != test_*.py && "$BASENAME" != *_test.py ]]; then
    exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"
OUTPUT=$(python3 -m pytest "$FILE_PATH" --tb=short -q 2>&1)
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    printf '%s\n' "$OUTPUT" >&2
    exit 2
fi
