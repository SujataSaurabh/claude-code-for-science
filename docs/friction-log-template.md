# Friction log template

A friction log is a structured record of moments where a tool did not behave the way you
expected. It is not a bug report — it captures confusion, surprises, and inefficiencies,
including cases where the tool worked correctly but the workflow felt wrong.

Friction logs are most useful when they are written immediately after the friction occurs,
while the specifics are fresh.

## How to use this template

Copy the entry template below for each friction moment. Fill in all fields. If you do not
have a suggested fix, write "unknown" — the observation is still useful.

One entry per moment. Do not combine multiple friction points into one entry.

---

## Entry template

```
### <short title describing the friction>

**Date:** YYYY-MM-DD

**Task:**
What were you trying to accomplish? Be specific — "add a docstring to reduce.py" is
more useful than "improve the code."

**Expected behavior:**
What did you expect the tool to do?

**Actual behavior:**
What did it actually do? Include any error messages or unexpected output verbatim.

**Severity:** low / medium / high

- low: minor inconvenience, worked around easily
- medium: required significant manual correction or wasted meaningful time
- high: produced incorrect output that I did not catch, or blocked progress entirely

**Suggested fix:**
What change to the tool, plugin, skill, documentation, or workflow would prevent this
friction? A vague suggestion is better than none.

**Workaround used:**
What did you actually do to get past this moment?
```

---

## Guidance on severity

Use **high** when: Claude produced output that was wrong in a way that was hard to detect
(e.g., changed an algorithm subtly, introduced a constant that was plausible but incorrect),
or when the friction blocked you from completing the task.

Use **medium** when: you had to redo work or manually fix output, but the error was obvious
once you looked.

Use **low** when: you noticed something annoying but fixed it quickly and it did not affect
your output.

---

## Sharing your log

If you are comfortable sharing, add entries to `docs/friction-log.md` in this repository and
open a pull request. Friction logs from multiple users are the primary source of signal for
improving this toolkit.
