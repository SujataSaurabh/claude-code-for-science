---
name: standards
description: "Apply scientific Python coding standards to a file or directory: type hints, NumPy-style docstrings, structured logging, and defensive error handling. Invoke automatically when editing pipeline code or explicitly with /sci:standards."
argument-hint: "[file-or-directory]"
user-invocable: true
allowed-tools: "Read Edit Bash(ruff *)"
---

Review and apply scientific Python standards to $ARGUMENTS (or the current file if no argument given).

Work through each of the following checks in order. For each issue found, explain the problem briefly, then make the fix.

## 1. Type annotations

Every function and method signature must have:
- Type hints on all parameters (including `self` only when non-trivially typed)
- A return type annotation (use `-> None` when nothing is returned)
- Use `from __future__ import annotations` at the top of files targeting Python 3.11+

Bad: `def calibrate(data, scale):`
Good: `def calibrate(data: np.ndarray, scale: float) -> np.ndarray:`

## 2. NumPy-style docstrings

Every public function needs a docstring with at least **Parameters** and **Returns** sections.
Use **Raises** when exceptions are documented. Use **Examples** for non-obvious usage.

```
def reduce(data: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Azimuthal integration of a 2D detector image.

    Parameters
    ----------
    data : np.ndarray
        2D array of pixel intensities, shape (H, W).
    mask : np.ndarray
        Boolean mask of valid pixels, shape (H, W). True = valid.

    Returns
    -------
    q_arr : np.ndarray
        Radial coordinate array, shape (N,).
    I_arr : np.ndarray
        Azimuthally averaged intensity, shape (N,).
    """
```

## 3. Structured logging

Replace every `print()` call with the module-level logger.

At module top (after imports): `log = logging.getLogger(__name__)`

- Info: `log.info("Processing %d pixels", n_pixels)`
- Debug: `log.debug("Calibration scale: %f", scale)`
- Error: `log.error("Failed to open file: %s", path)`
- Exception (inside except): `log.exception("Unexpected error during reduction")`

Do NOT use f-strings in log calls; use %-formatting so the string is only formatted if the level is enabled.

## 4. Defensive error handling

- Catch specific exception types, never bare `except:` or `except Exception:` without re-raising or logging.
- Log exceptions with `log.exception(...)` inside `except` blocks so the traceback is preserved.
- Validate array shapes at function entry when the shape matters for correctness.

Bad:
```python
try:
    result = process(data)
except:
    pass
```

Good:
```python
try:
    result = process(data)
except ValueError as exc:
    log.exception("Invalid data shape in process")
    raise
```

## 5. Constants

Any numeric literal that represents a physical or calibration constant must live in
`constants.py`, not inline in the code. Import it explicitly:

```python
from pipeline.constants import CALIBRATION_SCALE, RING_Q_VALUES
```

After all fixes are applied, run `ruff check` on the file and fix any remaining issues it reports.
