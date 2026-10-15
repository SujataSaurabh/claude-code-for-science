"""Static analysis tests for prompt-injection-relevant code patterns.

These tests inspect the pipeline source files using the ast module to verify
that no dangerous execution patterns are present. They do not call Claude or
require external services.

Run explicitly:
    pytest security/prompt-injection-harness/ -v

Not included in default testpaths (see pyproject.toml).
"""
from __future__ import annotations

import ast
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent.parent.parent / "example-pipeline" / "pipeline"

PIPELINE_SOURCES = list(PIPELINE_DIR.glob("*.py"))


def _parse_source(path: Path) -> ast.Module:
    return ast.parse(path.read_text(), filename=str(path))


def _all_call_names(tree: ast.Module) -> list[str]:
    """Return all function/method call names in the tree."""
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.append(func.id)
            elif isinstance(func, ast.Attribute):
                names.append(func.attr)
    return names


def test_pipeline_sources_found() -> None:
    """Sanity check: the pipeline directory contains Python files."""
    assert len(PIPELINE_SOURCES) > 0, (
        f"No .py files found in {PIPELINE_DIR}. Check that the path is correct."
    )


def test_no_eval_in_pipeline() -> None:
    """Pipeline source files must not call eval()."""
    for path in PIPELINE_SOURCES:
        tree = _parse_source(path)
        calls = _all_call_names(tree)
        assert "eval" not in calls, (
            f"{path.name}: eval() call found. Pipeline code must never evaluate "
            "strings as code — this pattern allows injection of arbitrary Python "
            "if attacker-controlled strings reach this call."
        )


def test_no_exec_in_pipeline() -> None:
    """Pipeline source files must not call exec()."""
    for path in PIPELINE_SOURCES:
        tree = _parse_source(path)
        calls = _all_call_names(tree)
        assert "exec" not in calls, (
            f"{path.name}: exec() call found. Same risk as eval()."
        )


def test_no_subprocess_in_pipeline() -> None:
    """Pipeline source files must not invoke subprocess or os.system."""
    dangerous = {"system", "popen", "run", "call", "check_output", "check_call", "Popen"}
    for path in PIPELINE_SOURCES:
        tree = _parse_source(path)
        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in ("subprocess", "os.system"), (
                        f"{path.name}: imports {alias.name}. Shell subprocess calls "
                        "must not appear in pipeline processing code."
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module in ("subprocess",):
                    for alias in node.names:
                        assert alias.name not in dangerous, (
                            f"{path.name}: imports subprocess.{alias.name}. "
                            "Shell calls must not appear in pipeline processing code."
                        )
        # Check calls
        calls = _all_call_names(tree)
        for name in dangerous:
            assert name not in calls, (
                f"{path.name}: call to {name}() detected. This could allow "
                "attacker-controlled data to reach a shell if array contents "
                "are formatted into the command."
            )


def test_no_pickle_loads_in_pipeline() -> None:
    """Pipeline source files must not deserialize pickle data."""
    for path in PIPELINE_SOURCES:
        tree = _parse_source(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "pickle":
                    for alias in node.names:
                        assert alias.name != "loads", (
                            f"{path.name}: imports pickle.loads. Deserializing "
                            "untrusted pickle data is arbitrary code execution."
                        )
        calls = _all_call_names(tree)
        assert "loads" not in calls or _no_pickle_loads_call(tree), (
            f"{path.name}: possible pickle.loads() call. Deserializing untrusted "
            "pickle data is arbitrary code execution."
        )


def _no_pickle_loads_call(tree: ast.Module) -> bool:
    """Return True if any 'loads' call is clearly not a pickle.loads call."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "loads":
                if isinstance(func.value, ast.Name) and func.value.id == "pickle":
                    return False
    return True


def test_no_shell_formatted_strings_in_pipeline() -> None:
    """Pipeline source files must not format data values into shell command strings.

    This is a heuristic check: looks for f-strings or %-formatting calls whose
    result is passed directly to a shell-invoking function.
    """
    shell_callers = {"system", "popen"}
    for path in PIPELINE_SOURCES:
        tree = _parse_source(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                call_name = None
                if isinstance(func, ast.Name):
                    call_name = func.id
                elif isinstance(func, ast.Attribute):
                    call_name = func.attr
                if call_name in shell_callers:
                    for arg in node.args:
                        assert not isinstance(arg, ast.JoinedStr), (
                            f"{path.name}: f-string passed directly to {call_name}(). "
                            "Formatting data values into shell commands enables injection."
                        )


def test_pipeline_only_uses_numpy_scipy() -> None:
    """Pipeline modules should only import from numpy, scipy, json, logging, pathlib, and stdlib.

    This verifies that no unexpected third-party library has been added that could
    introduce a network call or deserialization risk.
    """
    allowed_third_party = {"numpy", "scipy", "np"}
    for path in PIPELINE_SOURCES:
        if path.name == "__init__.py":
            continue
        tree = _parse_source(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    assert top in allowed_third_party or _is_stdlib(top), (
                        f"{path.name}: unexpected import '{alias.name}'. "
                        "Pipeline code should only use numpy, scipy, and stdlib."
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                top = node.module.split(".")[0]
                assert top in allowed_third_party or _is_stdlib(top), (
                    f"{path.name}: unexpected import from '{node.module}'. "
                    "Pipeline code should only use numpy, scipy, and stdlib."
                )


def _is_stdlib(name: str) -> bool:
    stdlib_modules = {
        "__future__", "abc", "ast", "collections", "contextlib", "copy", "datetime",
        "enum", "functools", "io", "itertools", "json", "logging", "math", "os",
        "pathlib", "re", "shutil", "signal", "sys", "tempfile", "time", "typing",
        "warnings", "pipeline",
    }
    return name in stdlib_modules
