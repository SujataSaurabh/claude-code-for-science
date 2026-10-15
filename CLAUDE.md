# claude-code-for-science

Starter kit for scientific Python data pipelines. The example pipeline generates and processes
synthetic beamline-style detector images — no real or proprietary data.

## Conventions

- All pipeline functions are type-annotated with NumPy-style docstrings (Parameters / Returns /
  Raises / Examples sections).
- Module-level logger: `log = logging.getLogger(__name__)`. No bare `print()` calls.
- Numeric constants live in `example-pipeline/pipeline/constants.py` only. Never hardcode magic
  numbers inline.
- Dead pixels are represented as a boolean mask (`True` = valid pixel). They are excluded from
  radial binning; they are never zeroed in the data array.
- Tests live in `example-pipeline/tests/`. Run with `pytest` from the repo root.
- The plugin is in `plugin/`. Skills are named `/sci:standards`, `/sci:new-flow`,
  `/sci:review-pipeline`.
