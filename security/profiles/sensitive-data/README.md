# Sensitive data profile

This profile is appropriate when working with proprietary, regulated, embargoed, or
otherwise sensitive data. It prevents Claude from taking any action that could transfer
data outside your local environment.

## Primary concern: data exfiltration

When Claude processes sensitive data, it has access to the content of any files it reads.
While Claude itself does not transmit data externally, a compromised session or a confused
agentic action could invoke a command that does. This profile blocks all network-capable
shell commands: curl, wget, rsync, scp, sftp, ssh.

It also blocks all git network operations (push, pull, fetch, remote) so that code
changes — which might include data snippets in comments, test fixtures, or log output —
cannot be pushed to a remote repository without your explicit action outside of Claude.

## What it allows

Only the minimum needed for development: running tests, linting, read-only git inspection,
and basic filesystem navigation.

## What it denies

- All file transfer commands (curl, wget, rsync, scp, sftp, ssh)
- All git network operations (push, pull, fetch, remote)
- All deletion (rm in any form)
- Package installation (pip, conda)
- Job scheduling (sbatch, srun, scancel)
- Permission changes (chmod, chown)
- Process termination (kill, killall)
- Privilege escalation (sudo, su)

## How to use

```
cp security/profiles/sensitive-data/settings.json .claude/settings.json
```

## Additional precautions

This settings file restricts what Claude can do via shell commands. It does not:

- Prevent Claude from reading files you point it to
- Prevent Claude from including file content in its responses
- Prevent you from copy-pasting Claude output to external services

For highly sensitive work, also consider:
- Running Claude Code in a network-isolated environment
- Reviewing Claude's session transcript before ending a session
- Using the prompt-injection harness to verify your pipeline code does not have
  patterns that could cause data to leak through generated output
