# Personal workstation profile

This profile is appropriate for working on your own machine with your own data. It allows common
development operations (Python, pip, pytest, ruff, read-only git, basic filesystem exploration)
and denies the most accident-prone destructive commands.

## What it allows

- Running Python scripts and the test suite
- Installing packages with pip
- Linting with ruff
- Read-only git operations (status, diff, log) and staging/committing
- Filesystem navigation (ls, find, cat, head, tail)

## What it denies

- `rm -rf` — mass recursive deletion
- `sudo` — privilege escalation
- Piped downloads (`curl ... | bash`, `wget ... | sh`) — arbitrary remote code execution
- World-writable chmod

## How to use

Copy this file to your project's `.claude/settings.json` for project-scoped restrictions, or to
`~/.claude/settings.json` to apply it to all Claude Code sessions on this machine.

```
cp security/profiles/personal/settings.json .claude/settings.json
```

When Claude attempts a denied command, it will be prompted to ask your permission first. You can
approve individual commands without removing the deny rule.

## Adjusting the allow list

The allow rules pre-approve commands so Claude does not ask for confirmation on every routine
operation. Add entries for tools you use frequently. Use specific patterns (`Bash(pytest *)`)
rather than broad ones (`Bash(*)`) so you are only bypassing prompts for things you actually
expect Claude to run.
