# Security

This directory contains tools for running Claude Code more safely in different scientific computing
environments. None of this is required for the plugin to work — it is supplementary material for
teams who need to think carefully about what Claude is allowed to do.

## Choosing a profile

| Profile | Use when |
|---------|----------|
| `profiles/personal/` | Your own workstation, only your own data, low-stakes experiments |
| `profiles/shared-cluster/` | An HPC login node or shared filesystem where others are affected by your actions |
| `profiles/sensitive-data/` | Working with proprietary, regulated, or embargoed data where accidental exfiltration or deletion would be serious |

Profiles are plain `settings.json` files. Copy the one you want to
`~/.claude/settings.json` (user-wide) or `.claude/settings.json` (project-only). Project settings
take precedence over user settings for conflicting keys.

## Guard hook

`guard-hooks/block-dangerous.sh` is a PreToolUse hook that intercepts Bash commands before
Claude runs them and blocks a set of known-dangerous patterns (mass deletion, pipe-to-shell
downloads, database drops). Install it by referencing it in your `.claude/settings.json` hooks
section. See `guard-hooks/README.md` for details.

The guard hook is not a security boundary — a sufficiently creative command will get through.
Its purpose is to catch the most common accidental or hallucinated dangerous operations during
normal agentic work.

## Prompt-injection harness

`prompt-injection-harness/test_prompt_injection.py` contains static-analysis tests that verify
the pipeline source code itself does not contain patterns that would execute attacker-controlled
input (no `eval`, no `exec`, no subprocess calls with unsanitized array data). Run it manually
with `pytest security/prompt-injection-harness/` — it is intentionally excluded from the default
`pytest` test collection so it does not slow down the normal development loop.

See `prompt-injection-harness/README.md` for background on why this matters for data pipelines.
