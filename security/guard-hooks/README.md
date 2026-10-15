# Guard hook: block-dangerous.sh

`block-dangerous.sh` is a PreToolUse hook that intercepts Bash commands before Claude executes
them and blocks a set of known-dangerous patterns.

## What it blocks

| Pattern | Reason |
|---------|--------|
| `rm -rf` | Recursive force deletion — high blast radius, hard to recover |
| `rm -r` | Recursive deletion without force flag |
| `curl \| bash`, `curl \| sh` | Pipe-to-shell download and execute |
| `wget \| bash`, `wget \| sh` | Same pattern with wget |
| `DROP TABLE`, `DROP DATABASE` | Destructive SQL |
| `> /dev/sda`, `> /dev/sd` | Writing directly to block devices |
| `chmod -R 777` | Mass world-writable permission change |
| `:(){ :|:& };:` | Fork bomb |

The list is conservative by design. It targets patterns that are almost never legitimate
in a scientific computing workflow and that cause serious, hard-to-reverse damage.

## What it does not block

This hook is not a security boundary. It does not:
- Block every possible dangerous command
- Prevent Claude from reading sensitive files
- Provide isolation between Claude and your filesystem

Use the security profiles (see `../profiles/`) in addition to this hook, not instead.

## How to install

Add the hook to your `.claude/settings.json` under the `hooks` key:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/claude-code-for-science/security/guard-hooks/block-dangerous.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

Replace `/path/to/claude-code-for-science` with the absolute path to this repo.

If you install the plugin with `--plugin-dir ./plugin`, the hook is NOT automatically
active — you must add it to settings separately, because the guard hook is a project-level
safety control, not part of the plugin itself.

## Behavior on block

When a blocked pattern is detected, the hook writes a human-readable reason to stderr and
exits with code 2. Claude sees the stderr message and knows the command was blocked; it
will typically ask for confirmation or propose an alternative.

## Behavior on parse failure

If the hook cannot parse the JSON sent on stdin, it exits 0 (allow). This fail-open
behavior ensures the hook never silently blocks commands due to an environment issue.
The hook writes a note to stderr so you can see parsing failed.
