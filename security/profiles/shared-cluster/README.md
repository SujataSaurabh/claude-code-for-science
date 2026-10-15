# Shared cluster profile

This profile is appropriate for HPC login nodes or shared filesystems where your actions can
affect other users. It is significantly more restrictive than the personal profile.

## Key restrictions beyond personal profile

- **No package installation** — pip and conda commands are denied. On shared clusters, packages
  should be installed via a controlled environment (module system, pre-built containers, or a
  dedicated install session without Claude). This prevents Claude from inadvertently breaking a
  shared environment or installing untrusted packages.

- **No job submission** — sbatch, srun, and scancel are denied. Job submission should be
  deliberate; Claude should not queue batch jobs on your behalf without explicit approval.

- **No permission changes** — chmod and chown are denied to prevent accidental permission
  changes that could expose data to other users or lock you out of files.

- **No process termination** — kill and killall are denied to prevent accidentally killing
  other users' processes.

## What it allows

- Running Python and the test suite within your current environment
- Read-only git and filesystem inspection
- Querying the scheduler (squeue, sacct) and module system to understand the environment

## How to use

```
cp security/profiles/shared-cluster/settings.json .claude/settings.json
```

This profile is intentionally conservative. If Claude needs to install a package or submit a
job during a session, approve that specific command manually rather than broadening the profile.

## Note on scratch and project directories

Claude Code's file editing tools (Edit, Write) are not restricted by this profile — Claude can
still create, modify, and delete files in your working directory. If you are working in a
shared project directory, consider also reviewing what directories Claude should have write
access to and raising that with your system administrator.
