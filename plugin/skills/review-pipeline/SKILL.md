---
name: review-pipeline
description: "Deep review of a scientific Python data pipeline file or directory for correctness, scientific Python standards, testability, and potential data quality issues. Delegates to the pipeline-reviewer agent."
argument-hint: "[file-or-directory]"
user-invocable: true
allowed-tools: "Read Grep Glob"
---

Use the pipeline-reviewer agent to thoroughly review the pipeline code at $ARGUMENTS.

Tell the agent:
- The target path: $ARGUMENTS
- To check for: type hints, NumPy-style docstrings, structured logging, error handling,
  consistent handling of invalid or missing data (exclude it, never overwrite it), named
  constants instead of magic numbers, seeded RNG for reproducibility, test coverage for edge
  cases, and any conventions in the project's `CLAUDE.md`.
- To produce a structured report with sections: Summary, Issues Found (severity: high/medium/low),
  and Suggested Next Steps.
