# claude-code-for-science

A starter kit for using Claude Code to write reliable scientific data-processing code in Python.

Many scientists write code every day to clean, process, and analyze their data, but have never had
formal software engineering training. The result is often code that works today but is hard to
test, hard to share, and hard to trust a year later. This kit helps close that gap. It gives
Claude Code a set of good habits — documentation, testing, clear structure, safe configuration —
and applies them automatically while you work.

The kit works for any scientific field that uses Python. The included example uses synthetic
X-ray detector images, but that is only a demonstration project. The tools themselves work just as
well for climate records, genomics tables, neural recordings, telescope images, survey data, or
anything else you process with Python.

This is an independent community project. It is not an official Anthropic product.

---

## Contents

1. [Who this is for](#who-this-is-for)
2. [What is in this repository](#what-is-in-this-repository)
3. [Requirements](#requirements)
4. [Quick start: try the example in 5 minutes](#quick-start-try-the-example-in-5-minutes)
5. [Using the plugin in your own project](#using-the-plugin-in-your-own-project)
6. [The three commands](#the-three-commands)
7. [Automatic checks](#automatic-checks)
8. [Writing a CLAUDE.md for your project](#writing-a-claudemd-for-your-project)
9. [Examples from different fields](#examples-from-different-fields)
10. [Security profiles for shared computers](#security-profiles-for-shared-computers)
11. [Limitations](#limitations)
12. [Troubleshooting](#troubleshooting)
13. [Workshop materials and feedback](#workshop-materials-and-feedback)
14. [Contributing](#contributing)
15. [License](#license)

---

## Who this is for

- Researchers, postdocs, graduate students, and staff scientists who write Python to process data.
- Research software engineers who want to help their teams adopt consistent practices.
- Instructors running training sessions on AI-assisted coding for scientists.

You do not need to be an experienced software engineer. You should be comfortable running
commands in a terminal and have Claude Code installed.

---

## What is in this repository

| Folder or file          | What it is                                                                 |
|-------------------------|----------------------------------------------------------------------------|
| `plugin/`               | The Claude Code plugin. This is the main product: commands, a review agent, and automatic checks. Works with any Python project. |
| `example-pipeline/`     | A small demonstration pipeline that processes synthetic detector images. Use it to practice. |
| `security/`             | Example Claude Code settings for different environments (personal laptop, shared cluster, sensitive data), plus guard hooks. |
| `workshop/`             | Materials for a 90-minute hands-on session, including pre- and post-surveys. |
| `docs/`                 | Tutorials, an annotated explanation of `CLAUDE.md`, and a friction log template. |
| `CLAUDE.md`             | The project instructions Claude Code reads for this repository. A working example you can copy. |
| `pyproject.toml`        | Python package configuration and tool settings. |

---

## Requirements

- Python 3.11 or newer
- Claude Code, installed and signed in
- Git

The example pipeline uses only `numpy` and `scipy`. The automatic checks use `ruff` (a fast Python
linter) and `pytest` (a testing tool). All of these are installed in the quick start below.

---

## Quick start: try the example in 5 minutes

The fastest way to understand the kit is to run it on the included example before using it on your
own work. Nothing here touches your own files.

**1. Get the code and install it**

```bash
git clone https://github.com/sujatasaurabh/claude-code-for-science.git
cd claude-code-for-science
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

**2. Run the example pipeline**

```bash
python example-pipeline/run_pipeline.py
```

This generates a synthetic detector image containing ring patterns, applies a calibration and a
dead-pixel mask, reduces the 2D image to a 1D intensity curve, and writes a short summary of the
peaks it found. Each stage logs what it is doing.

**3. Run the tests**

```bash
pytest
```

All tests should pass. They check, for example, that the rings placed in the synthetic image are
found again at the right positions after processing.

**4. Start Claude Code with the plugin loaded**

Make sure you are still in the `claude-code-for-science` folder and your virtual environment is
active, then run:

```bash
claude --plugin-dir ./plugin
```

**5. Try a command**

Inside Claude Code, type `/sci:` and you should see three commands appear. Try:

```
/sci:review-pipeline example-pipeline/pipeline/reduce.py
```

Claude will review the file and report what is good and what could be improved.

---

## Using the plugin in your own project

Once you have tried the example, you can use the plugin with your own code. There are two ways.

**Option A: Load it for a session (good for trying it out)**

From your own project folder, point Claude Code at the plugin folder in this repository:

```bash
cd ~/my-research-project
claude --plugin-dir ~/path/to/claude-code-for-science/plugin
```

The commands and automatic checks are available for that session only.

**Option B: Install it from GitHub (good for everyday use)**

This repository is also set up as a Claude Code plugin marketplace. Inside Claude Code, run:

```
/plugin marketplace add sujatasaurabh/claude-code-for-science
/plugin install sci@sci-pipeline-tools
```

The marketplace name is defined in `.claude-plugin/marketplace.json`. After installing, the
commands are available in every project. You can manage installed plugins with the `/plugin`
command.

**Before you start in your own project**

- Install `ruff` and `pytest` in the environment you use for that project
  (`pip install ruff pytest`), so the automatic checks can run.
- Start Claude Code from the root folder of your project, with that environment active.
- Commit your work to Git first. That way you can review every change Claude makes with
  `git diff` and undo anything you do not want.

---

## The three commands

### `/sci:standards` — apply good coding practices

Asks Claude to bring code up to a consistent standard:

- Type hints on all function inputs and outputs
- NumPy-style docstrings with Parameters, Returns, Raises, and Examples sections
- Logging through `logging.getLogger(__name__)` instead of `print()`
- Specific error handling instead of bare `except:` blocks
- Named, documented constants instead of unexplained numbers in the code

**Example.** You have an old script that works but is hard to read:

```
/sci:standards analysis/clean_temperatures.py
```

Before:

```python
def clean(d):
    d = d[d > -90]
    print("removed bad values")
    return d * 1.8 + 32
```

After (typical result):

```python
import logging

import numpy as np

from analysis.constants import MIN_VALID_TEMPERATURE_C

log = logging.getLogger(__name__)


def clean(temperatures_c: np.ndarray) -> np.ndarray:
    """Remove invalid readings and convert from Celsius to Fahrenheit.

    Parameters
    ----------
    temperatures_c : np.ndarray
        Temperature readings in degrees Celsius.

    Returns
    -------
    np.ndarray
        Valid readings in degrees Fahrenheit.

    Examples
    --------
    >>> clean(np.array([20.0, -999.0]))
    array([68.])
    """
    valid = temperatures_c[temperatures_c > MIN_VALID_TEMPERATURE_C]
    log.info("Removed %d invalid readings", temperatures_c.size - valid.size)
    return valid * 9 / 5 + 32
```

The behavior is the same. The code is now readable, documented, and easier to test.

### `/sci:new-flow <name>` — create a new processing step

Creates a new pipeline stage and a matching test file, already following the standards above.

**Example.** You need a step that removes background signal from your measurements:

```
/sci:new-flow background-subtract
```

Claude first asks you to describe what the step should do scientifically: its inputs and
outputs, any constants involved, and a case where you know the right answer. Then it finds where
your project keeps its processing code and tests, and creates:

- `background_subtract.py` with a module logger, typed function signatures, and docstrings
- `test_background_subtract.py` with a starting set of tests, including one for your
  known-answer case

Hyphens in the name become underscores, so the files are valid Python modules. You supply the
science; the structure is handled for you.

### `/sci:review-pipeline <path>` — get a code review

Sends the file to a dedicated review agent that reads it carefully and reports problems in plain
language, such as missing tests, unexplained constants, unsafe error handling, or logic that is
hard to follow. It does not change your code unless you ask it to.

**Example.**

```
/sci:review-pipeline analysis/fit_peaks.py
```

Typical findings:

- "Line 42 uses the number 0.0254 with no explanation. Move it to a named constant."
- "`fit_peaks()` has no tests. Consider testing it with a synthetic peak at a known position."
- "The bare `except:` on line 71 hides all errors, including typos. Catch the specific exception
  you expect."

---

## Automatic checks

The plugin includes two hooks: small scripts that Claude Code runs automatically after it edits a
file. You do not need to do anything to use them.

| When                                  | What runs | What happens                                         |
|---------------------------------------|-----------|------------------------------------------------------|
| Claude edits any `.py` file           | `ruff check` | If ruff finds problems, the report goes back to Claude, which fixes them. |
| Claude edits a test file (`test_*.py`) | `pytest` on that file | If tests fail, the output goes back to Claude, which investigates. |

This means many mistakes — unused imports, undefined names, broken tests — are caught and fixed
while you work, rather than discovered later.

The hooks only report problems. They do not rewrite your files on their own; Claude makes the fix
in a normal, visible edit.

If `ruff` or `pytest` is not installed in your active environment, the checks cannot run. See
[Troubleshooting](#troubleshooting).

---

## Writing a CLAUDE.md for your project

`CLAUDE.md` is a plain text file in the root of your project that Claude Code reads at the start of
every session. It tells Claude how your project works: how to run it, how to test it, and which
conventions to follow.

The `CLAUDE.md` in this repository is a working example. To use it in your own project:

1. Copy it into your project's root folder.
2. Replace the description with a few sentences about your project.
3. Update the commands so they match how you run and test your code.
4. Keep the conventions you want, remove the rest, and add your own.

Keep it short and specific. Claude reads the whole file every session, so a few precise
instructions work better than pages of general advice. Good things to include:

- The exact commands to install, run, test, and lint
- Conventions specific to your data (for example, "missing values are stored as NaN, never as
  -999")
- Rules about dependencies (for example, "ask before adding new packages")
- Things Claude should not do (for example, "never modify files in `raw_data/`")

For a section-by-section explanation of why each part matters, see
`docs/annotated-claude-md.md`.

---

## Examples from different fields

The plugin does not know or care what your data represents. Here is how researchers in three
different fields might use it.

### Climate science: cleaning weather station records

Ana processes temperature records from hundreds of weather stations. Her scripts have grown over
several years and nobody else in her group can follow them.

1. She copies `CLAUDE.md` into her project and adds: "Missing values are stored as NaN. Station
   IDs are strings, never integers. Raw files in `data/raw/` must never be modified."
2. She runs `/sci:review-pipeline scripts/merge_stations.py`. The review points out that a
   hardcoded value of `-9999` is used to mark missing data in one place and `NaN` in another.
3. She runs `/sci:standards scripts/merge_stations.py` to add documentation and replace the
   scattered numbers with named constants.
4. She runs `/sci:new-flow detect-outliers` to add a new step that flags suspicious readings,
   with tests that use a small synthetic temperature series containing a known spike.

Result: the merging logic is documented, the missing-value handling is consistent, and the new
outlier step is tested from day one.

### Biology: analyzing plate reader measurements

Ben runs experiments in 96-well plates and exports absorbance readings as CSV files. He analyzes
them with a single long script.

1. He asks Claude to split the script into stages: load, normalize to control wells, fit growth
   curves, and summarize. He uses `/sci:new-flow` for each stage so every one gets its own tests.
2. While Claude writes the normalization step, the ruff hook catches an undefined variable left
   over from the old script. Claude fixes it before Ben notices.
3. He writes a test with a synthetic plate where the expected growth rates are known in advance,
   so he can confirm the curve fitting is correct.

Result: when a reviewer asks how the growth rates were calculated, Ben can point to documented,
tested code.

### Neuroscience: filtering electrophysiology recordings

Chen records neural signals and applies filters before detecting spikes. Small changes to filter
settings have caused hard-to-trace differences in results.

1. She uses `/sci:standards` on her filtering module. All filter cutoffs and sampling rates move
   into a documented constants file.
2. She asks Claude to add tests that run each filter on a synthetic signal with known frequency
   content and check that the right frequencies are removed.
3. Later, when a colleague changes a cutoff value, the pytest hook runs automatically and shows
   which tests are affected.

Result: filter settings are visible in one place, and any change that alters results is caught
by the tests.

### The common pattern

In every field, the workflow is the same:

1. Describe your project and conventions in `CLAUDE.md`.
2. Use `/sci:review-pipeline` to find problems in existing code.
3. Use `/sci:standards` to clean it up.
4. Use `/sci:new-flow` for new steps, so tests exist from the start.
5. Let the automatic checks catch mistakes as you go.
6. Test with synthetic data where you know the right answer in advance.

---

## Security profiles for shared computers

Claude Code can read files, run commands, and access the network, within the permissions you give
it. On a personal laptop, the defaults are usually fine. On a shared computing cluster, or when
working with sensitive data, you should be more careful.

The `security/profiles/` folder contains three example settings files:

| Profile          | Use it when                                                        |
|------------------|--------------------------------------------------------------------|
| `personal`       | You work on your own machine with your own data.                   |
| `shared-cluster` | You work on a computer shared with other users, such as an HPC cluster. |
| `sensitive-data` | Your data is confidential, regulated, or under embargo.            |

Each profile has a `README.md` explaining every setting and the risk it addresses. To use one,
copy its `settings.json` into your project's `.claude/` folder, then read its README and adjust it
to your situation.

The `security/guard-hooks/` folder contains an example hook that blocks risky shell commands
before they run, such as `rm -rf`, piping a download into `bash`, or `chmod -R 777`.

The `security/prompt-injection-harness/` folder contains offline tests that check the pipeline
code for patterns that would let instructions hidden in data files act as commands (such as
`eval`, `exec`, or passing data into shell commands). They make no calls to Claude. Run them with
`pytest security/prompt-injection-harness/`; see its README for details.

---

## Limitations

- **Python only.** The standards and automatic checks assume Python tools. They do not apply to
  R, Julia, MATLAB, or other languages.
- **Claude can make mistakes.** The commands and checks reduce errors, but they do not replace
  your scientific judgment. Review changes before relying on them, especially changes to
  calculations.
- **Tests are only as good as their design.** The kit makes writing tests easier, but you still
  need to decide what correct behavior looks like for your science.
- **The example is synthetic.** The example pipeline is simplified for teaching and is not
  intended for analyzing real experimental data.

---

## Troubleshooting

**The `/sci:` commands do not appear.**
Make sure you started Claude Code with `--plugin-dir` pointing at the `plugin` folder, or that you
installed the plugin with `/plugin install`. Restart Claude Code after installing.

**The automatic checks never seem to run.**
The most common cause is that `ruff` or `pytest` is not installed in the environment Claude Code
is running in. Activate your project's virtual environment before starting Claude Code, and check
with `ruff --version` and `pytest --version`.

**`pip install -e ".[dev]"` fails.**
Check that you are using Python 3.11 or newer (`python --version`) and that you are running the
command from the root of this repository.

**Claude Code asks for permission often.**
This is expected. Claude Code asks before running commands or changing settings. You can approve
actions one at a time, or adjust permissions in your settings. For shared or sensitive
environments, approving one at a time is safer.

---

## Workshop materials and feedback

The `workshop/` folder contains a 90-minute hands-on curriculum built around this repository,
with short surveys to run before and after the session. Instructors are welcome to use and adapt
it.

If something in this kit was confusing, slow, or did not work as expected, that information is
valuable. Use `docs/friction-log-template.md` to record it, and open an issue in this repository.
Specific notes — what you tried, what you expected, and what actually happened — are the most
useful.

---

## Contributing

Contributions are welcome, especially:

- Small examples from other scientific fields
- Improvements to the commands and review agent
- Corrections to documentation
- Reports of anything that did not work

Please open an issue to discuss larger changes before starting. All code contributions should
follow the conventions in `CLAUDE.md` and include tests.

---

## License

Apache License 2.0. See `LICENSE` for details.
