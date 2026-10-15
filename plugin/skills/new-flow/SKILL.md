---
name: new-flow
description: "Scaffold a new data processing stage in the current Python project. Asks what the stage should do scientifically, then creates a typed, documented Python module and a matching pytest test file following scientific Python conventions."
argument-hint: "[flow-name]"
user-invocable: true
allowed-tools: "Read Glob Grep Write Edit Bash(mkdir *)"
---

Scaffold a new pipeline stage named "$ARGUMENTS".

## Step 1: Normalize the name

Python module names cannot contain hyphens or spaces. Derive `{module}` from "$ARGUMENTS":

- lowercase it
- replace hyphens and spaces with underscores
- e.g. `background-subtract` → `background_subtract`

If `{module}` is still not a valid Python identifier (for example it starts with a digit), stop
and ask the user for a different name. Use `{module}` for every file name and import below;
use the original "$ARGUMENTS" only in human-readable text.

## Step 2: Find where stages and tests live

Do not assume a layout. Work it out from the current project:

1. Read `CLAUDE.md` and `pyproject.toml` (or `setup.cfg` / `setup.py`) if present.
2. `{src_dir}`: the package directory holding the existing processing stages, i.e. a directory
   with an `__init__.py` next to other stage modules. Check `[tool.setuptools.packages.find]`
   and `src/` layouts. `{package}` is its import name.
3. `{tests_dir}`: from `[tool.pytest.ini_options] testpaths`, otherwise an existing `tests/`
   directory, otherwise `tests/` at the project root.
4. `{constants}`: an existing constants module in `{package}` (e.g. `constants.py`), if any.

If there is no clear package, or more than one candidate, ask the user where the stage should
go. If `{src_dir}/{module}.py` or `{tests_dir}/test_{module}.py` already exists, stop and tell
the user; never overwrite it.

## Step 3: Ask what the stage should do

Before writing any files, ask the user to describe the stage scientifically, then wait for the
answer:

- What does it do to the data, in a sentence or two?
- What are the inputs and outputs (type, shape, units)?
- Are there parameters or physical constants involved, with their values and units?
- Is there a case where the right answer is known in advance (for example, a synthetic input
  with a known peak, spike, or frequency)? This becomes the first real test.

The user supplies the science; you supply the structure. If the answer describes a specific
method, implement it. If it is vague, leave a `TODO` for the transformation rather than
inventing the science.

## Step 4: Create the module, `{src_dir}/{module}.py`

Adapt the signature, docstring, and validation to the inputs and outputs the user described.
The structure must stay the same: module docstring, module logger, type hints, NumPy-style
docstring, input validation, %-style log calls.

```python
"""{Stage title} pipeline stage.

One-sentence description of what this stage does, from the user's answer.
"""
from __future__ import annotations

import logging

import numpy as np

log = logging.getLogger(__name__)


def process(data: np.ndarray) -> np.ndarray:
    """{What the stage does, from the user's answer}.

    Parameters
    ----------
    data : np.ndarray
        {Description, shape, and units.}

    Returns
    -------
    np.ndarray
        {Description, shape, and units.}

    Raises
    ------
    ValueError
        If ``data`` does not have the expected shape.
    """
    if data.ndim != 1:
        raise ValueError(f"expected a 1D array, got shape {data.shape}")

    log.info("Running {module} on array of shape %s", data.shape)

    # TODO: implement transformation
    result = data.copy()

    log.debug("{module} complete; output shape %s", result.shape)
    return result
```

Numeric constants: if `{constants}` exists, add any new constants there (with a comment giving
units and meaning) and import them. If it does not exist, ask the user before creating one. Do
not hardcode magic numbers in the stage.

## Step 5: Create the tests, `{tests_dir}/test_{module}.py`

```python
"""Tests for the {module} pipeline stage."""
from __future__ import annotations

import numpy as np
import pytest

from {package}.{module} import process

RNG_SEED = 0  # or import the project's seed constant from {constants} if it has one


@pytest.fixture
def sample_data() -> np.ndarray:
    """Return a small, seeded synthetic input."""
    rng = np.random.default_rng(RNG_SEED)
    return rng.standard_normal(64)


def test_process_returns_same_shape(sample_data: np.ndarray) -> None:
    result = process(sample_data)
    assert result.shape == sample_data.shape


def test_process_raises_on_bad_shape() -> None:
    with pytest.raises(ValueError, match="shape"):
        process(np.zeros((4, 4)))
```

Match the test inputs to the signature from Step 4. If the user gave a known-answer case, add a
test for it that builds the synthetic input and checks the output against the known answer
within a stated tolerance.

## Step 6: Report

Tell the user which files were created or edited and remind them to:
1. Replace any `TODO` with the actual transformation logic.
2. Add domain-specific tests beyond the shape checks.
3. Call the new stage from the project's pipeline entry point (for example `run_pipeline.py`)
   if it should run automatically.
