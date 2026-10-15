# Annotated CLAUDE.md — why each line exists

This document walks through the project's `CLAUDE.md` line by line and explains the purpose
of each section. Use it as a template for writing your own CLAUDE.md.

---

## What CLAUDE.md is

CLAUDE.md is a file in the root of your repository that Claude Code reads at the start of
every session. It is plain markdown. Its purpose is to give Claude context that cannot be
derived from reading the code — the *why* behind conventions, constraints specific to your
domain, and pointers to where things live.

A well-written CLAUDE.md is short. It is not a README. It does not explain setup instructions
to a human reader. It is a briefing for an AI assistant that already knows how to write
Python but does not know your project's conventions or the physical constraints of your
detector.

---

## The full CLAUDE.md

```markdown
# claude-code-for-science

Starter kit for scientific Python data pipelines. Pipeline runs on synthetic beamline data.

## Conventions

- All pipeline functions: type-annotated, NumPy-style docstrings, module-level logger
- Numeric constants → `example-pipeline/pipeline/constants.py` only
- Dead pixels represented as a boolean mask (True = valid), never zeroed
- Tests in `example-pipeline/tests/`; run with `pytest` from repo root
- The plugin is in `plugin/`. Skills: /sci:standards, /sci:new-flow, /sci:review-pipeline
```

---

## Line-by-line annotations

### `# claude-code-for-science`

The heading names the project. Claude uses this to disambiguate when multiple CLAUDE.md files
are in scope (e.g., a user-level CLAUDE.md and a project-level one).

---

### `Starter kit for scientific Python data pipelines. Pipeline runs on synthetic beamline data.`

One sentence of project context. The phrase "synthetic beamline data" is important — it tells
Claude that the data is generated, not real, so Claude does not need to worry about data
privacy constraints when reading or printing pipeline outputs. If your project used real
detector data, you would write something like "data files are proprietary and must not be
printed in full or written to new locations" instead.

---

### `## Conventions`

This section is where most of the value lives. Conventions are things Claude would not know
from reading the code alone, or things you want applied consistently that Claude might
otherwise vary.

---

### `- All pipeline functions: type-annotated, NumPy-style docstrings, module-level logger`

Three style requirements in one line. Being explicit here means Claude applies these when it
writes or edits any function, not just when you ask. Without this, Claude might:
- Write Google-style docstrings (it sees both styles in its training data)
- Use `print()` instead of `logging`
- Skip type hints on functions it considers "obvious"

The module-level logger pattern (`log = logging.getLogger(__name__)`) is domain-specific
enough that Claude needs to be told it is the convention here.

---

### `- Numeric constants → example-pipeline/pipeline/constants.py only`

This is a constraint that cannot be inferred from reading one file — it requires knowing the
project's architecture. Without this line, Claude will sometimes hardcode numbers inline
when adding new logic. The `→` is deliberate: it is more scannable than "Numeric constants
should be placed in..." and Claude reads markdown structure well.

---

### `- Dead pixels represented as a boolean mask (True = valid), never zeroed`

This is the most domain-specific line in the file. It describes a physics/engineering
invariant: dead pixels are real pixels with no valid signal, not pixels with zero signal.
If Claude zeroed them, downstream peak-finding would see spurious zeros affecting the
azimuthal average. This line prevents Claude from "fixing" the code to zero dead pixels
when it sees `mask[row, col] = False` and finds that confusing.

The parenthetical `(True = valid)` is there because the boolean convention is non-obvious.
`True = valid` reads more naturally to a new reader than `False = dead`.

---

### `- Tests in example-pipeline/tests/; run with pytest from repo root`

Two facts in one bullet:
1. Where tests live — so Claude knows where to look when asked about tests and where to put
   new test files
2. How to run them — Claude Code can run `pytest` from the terminal and the hook system also
   calls pytest; this ensures the invocation is consistent

"from repo root" matters because pytest's test discovery and `pyproject.toml` path
configuration depend on where you run it from.

---

### `- The plugin is in plugin/. Skills: /sci:standards, /sci:new-flow, /sci:review-pipeline`

This tells Claude that skills exist and names them. Without this, if you ask Claude "apply
the standards skill to this file," Claude might not know a skill called `/sci:standards`
exists or that it should invoke it. Naming all three also prevents Claude from trying to
invent a `/sci:calibrate` skill if you ask it to do something calibration-related.

---

## What CLAUDE.md does NOT contain

By design, this CLAUDE.md does not include:

- **Setup instructions** — those are in README.md for humans to read
- **A list of every file in the project** — Claude reads the filesystem; it does not need a
  map in CLAUDE.md
- **Plugin loading instructions** (`claude --plugin-dir ./plugin`) — that is a human step,
  not a Claude instruction
- **Explanations of what each module does** — Claude reads the modules

The rule of thumb: if Claude could figure it out by reading a file, do not put it in
CLAUDE.md. CLAUDE.md is for constraints, conventions, and context that are not in the code.

---

## Writing your own CLAUDE.md

A useful structure:

```markdown
# <project name>

<one sentence: what does this project do, and is there anything about the data or environment
Claude should know upfront (sensitive data, unusual conventions, hardware constraints)>

## Conventions

- <coding style: docstring format, logging pattern, type hint requirement>
- <where constants/config live>
- <any domain-specific invariant that looks wrong but is intentional>
- <where tests live and how to run them>
- <any plugin or skills available>
```

Keep it to one screen. If it is longer, you are probably writing documentation for humans,
not a briefing for Claude.
