# Workshop: Claude Code for Scientific Python Pipelines

A 90-minute hands-on workshop for scientists and research software engineers who want to use
Claude Code to write, refactor, and audit data pipelines.

## Who this is for

Scientists and engineers who:
- Write Python data processing pipelines (detector data, simulation output, instrument feeds)
- Are comfortable with the command line but may not have a formal software engineering background
- Want to use AI coding tools more effectively and more safely

No prior experience with Claude Code is required. Basic Python and familiarity with the
terminal are expected.

## What participants will do

1. Install Claude Code and the `sci` plugin from this repository
2. Apply the `/sci:standards` skill to an existing pipeline module to add type hints, logging,
   and NumPy docstrings
3. Use `/sci:new-flow` to scaffold a new pipeline stage from scratch
4. Run `/sci:review-pipeline` and interpret the structured review output
5. Fill out a friction log entry documenting one thing that did not work as expected

## What participants will walk away with

- A working Claude Code setup with the `sci` plugin active
- Practical experience with three domain-specific skills
- A friction log entry that contributes to improving this toolkit
- An understanding of where Claude Code adds real value (boilerplate, docstrings, review) and
  where it requires careful oversight (domain-specific constants, algorithm correctness)

## Prerequisites

- Python 3.11+ installed
- `git` installed
- Claude Code installed (`npm install -g @anthropic-ai/claude-code` or via the desktop app)
- An Anthropic account with Claude Code access
- This repository cloned locally

## Setup before the workshop

```
git clone https://github.com/sujatagoswami/claude-code-for-science
cd claude-code-for-science
pip install -e ".[dev]"
pytest  # verify 29 tests pass
claude --plugin-dir ./plugin
```

When Claude Code opens, run `/sci:standards --help` to confirm the plugin loaded.

## Materials

- `curriculum.md` — facilitator guide with timed segments
- `pre-survey.md` — send to participants before the workshop
- `post-survey.md` — collect at the end of the workshop
- `../docs/friction-log-template.md` — blank friction log for the exercise
