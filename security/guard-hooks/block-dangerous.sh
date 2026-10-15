#!/usr/bin/env bash
# PreToolUse hook: block known-dangerous shell command patterns.
# Reads hook JSON from stdin; parses with python3 (no jq dependency).
# On match: writes reason to stderr, exits 2 (blocks the command).
# On parse failure: exits 0 (fail open) with a note to stderr.
# No set -e; exit codes are explicit.

INPUT=$(cat)

COMMAND=$(printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    cmd = d.get('tool_input', {}).get('command', '')
    print(cmd)
except Exception:
    sys.stderr.write('block-dangerous: could not parse hook JSON, allowing\n')
    sys.exit(0)
")

PARSE_EXIT=$?
if [[ $PARSE_EXIT -ne 0 ]]; then
    exit 0
fi

if [[ -z "$COMMAND" ]]; then
    exit 0
fi

# Check deny patterns. Each check writes a reason to stderr and exits 2 on match.

if printf '%s' "$COMMAND" | grep -qE 'rm[[:space:]]+-[a-zA-Z]*r[a-zA-Z]*f|rm[[:space:]]+-[a-zA-Z]*f[a-zA-Z]*r'; then
    printf 'BLOCKED: rm -rf detected. Use targeted deletion instead.\n' >&2
    exit 2
fi

if printf '%s' "$COMMAND" | grep -qE 'rm[[:space:]]+-[a-zA-Z]*r[^f]|rm[[:space:]]+-r([[:space:]]|$)'; then
    printf 'BLOCKED: recursive rm detected. Use targeted deletion instead.\n' >&2
    exit 2
fi

if printf '%s' "$COMMAND" | grep -qE '(curl|wget)[^|]*\|[[:space:]]*(bash|sh)'; then
    printf 'BLOCKED: pipe-to-shell download detected (curl/wget | bash/sh).\n' >&2
    exit 2
fi

if printf '%s' "$COMMAND" | grep -qiE 'DROP[[:space:]]+(TABLE|DATABASE|SCHEMA)'; then
    printf 'BLOCKED: destructive SQL statement detected (DROP TABLE/DATABASE).\n' >&2
    exit 2
fi

if printf '%s' "$COMMAND" | grep -qE '>[[:space:]]*/dev/sd'; then
    printf 'BLOCKED: redirect to block device detected.\n' >&2
    exit 2
fi

if printf '%s' "$COMMAND" | grep -qE 'chmod[[:space:]]+-R[[:space:]]+777|chmod[[:space:]]+777[[:space:]]+-R'; then
    printf 'BLOCKED: mass world-writable chmod detected.\n' >&2
    exit 2
fi

if printf '%s' "$COMMAND" | grep -qF ':(){ :|:& };:'; then
    printf 'BLOCKED: fork bomb pattern detected.\n' >&2
    exit 2
fi

exit 0
