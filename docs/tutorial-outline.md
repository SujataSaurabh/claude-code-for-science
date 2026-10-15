# Tutorial outline: Claude Code for scientific data pipelines

This is an outline for a written tutorial aimed at scientists and research software engineers.
The tutorial is longer and more self-paced than the workshop curriculum.

---

## 1. Why use Claude Code for scientific pipelines?

- The problem: pipelines written under deadline pressure lack type hints, docstrings, logging,
  and tests — making them hard to hand off or reproduce
- What Claude Code does well in this context: boilerplate generation, docstrings, logging
  scaffolding, test skeleton writing, code review
- What Claude Code does not do well: domain-specific algorithm correctness, verifying that
  physics is right, understanding instrument-specific data quirks
- The agentic loop: edit → lint → test → repeat, with hooks automating the feedback cycle

---

## 2. Anatomy of a CLAUDE.md

- What the file is and when Claude reads it
- The difference between context for Claude and documentation for humans
- Walking through the project's CLAUDE.md line by line
  (see `docs/annotated-claude-md.md` for the full annotation)
- Common mistakes: too long, includes setup instructions, duplicates what's in the code
- Template: one paragraph of project context, one conventions section, five to eight bullets

---

## 3. Anatomy of a skill

- What a skill is: a SKILL.md file in the plugin directory that gives Claude specialized
  instructions for a particular task
- SKILL.md structure: frontmatter (name, description, argument-hint, user-invocable,
  allowed-tools) and a body with the instructions
- Walking through `/sci:standards`: what the skill asks Claude to do, in what order
- Walking through `/sci:new-flow`: how it takes an argument (the stage name) and uses it
- Walking through `/sci:review-pipeline`: how it delegates to the pipeline-reviewer agent
- When to write a new skill vs. just asking Claude directly: repetitive structured tasks
  benefit from a skill; one-off analysis does not

---

## 4. Setting up the plugin

- Plugin directory structure: `.claude-plugin/plugin.json`, `skills/`, `agents/`, `hooks/`
- Loading for one session: `claude --plugin-dir ./plugin`
- Loading persistently: copy to `~/.claude/skills/sci/`
- Using the marketplace: `/plugin marketplace add sujatagoswami/claude-code-for-science`,
  then `/plugin install sci@sci-pipeline-tools`
- Verifying the plugin loaded: type `/sci` and see the skill suggestions appear
- How hooks work: `PostToolUse` fires after each Edit/Write; ruff-check.sh and
  pytest-check.sh run and surface failures in the conversation via exit 2 + stderr

---

## 5. Hands-on example: the synthetic beamline pipeline

- Overview of the pipeline: generate → calibrate → reduce → summarize
- Running the pipeline: `python example-pipeline/run_pipeline.py`
- Running the tests: `pytest`
- Exercise 1: run `/sci:standards` on `calibrate.py`, review the output, check the tests pass
- Exercise 2: run `/sci:new-flow normalize` to scaffold a normalization stage
- Exercise 3: run `/sci:review-pipeline example-pipeline/pipeline/` and pick one finding
  to act on

---

## 6. Common patterns for scientific Python

### Seeded RNG for reproducible tests

Using `np.random.default_rng(seed)` instead of `np.random.seed()` — why the Generator API
is preferred, how to pass the seed as a parameter for testability.

### Boolean masks instead of zeroing

The dead-pixel pattern: `mask = np.ones(shape, dtype=bool); mask[dead_row, dead_col] = False`
and then `image[mask]` to exclude dead pixels from computation. Why zeroing is wrong
(introduces a false minimum into the distribution).

### Constants module

Why all numeric constants go in `constants.py`: makes changes auditable, prevents drift
between production code and tests, makes the domain semantics explicit.

### Module-level logger

`log = logging.getLogger(__name__)` in every module. Using `log.info` / `log.warning` instead
of `print`. Why this matters: log levels are filterable, logging is structured and redirectable,
print output disappears in batch jobs.

### NumPy-style docstrings

The Parameters / Returns / Raises / Examples structure. Why it is preferred over Google-style
for scientific code: renders well in Sphinx, integrates with numpy's own documentation, familiar
to most scientific Python users.

---

## 7. Using security profiles

- When to use which profile (personal vs. shared-cluster vs. sensitive-data)
- How to apply a profile: copy `settings.json` to `.claude/settings.json`
- The guard hook: what it blocks, how to install it, what it does not protect against
- Static analysis with the prompt-injection harness: `pytest security/prompt-injection-harness/`
