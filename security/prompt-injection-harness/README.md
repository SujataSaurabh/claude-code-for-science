# Prompt injection harness

## What is prompt injection in a data pipeline?

Prompt injection occurs when attacker-controlled content in an external input is interpreted
as instructions rather than data. In a language model context, this typically means content
in a file, database record, or API response that contains text like "Ignore previous
instructions and instead..." — causing the model to change its behavior.

For scientific data pipelines, the risk is more subtle. If Claude is asked to help process
or summarize data files, and those files contain crafted text, the text could influence what
Claude does next. For example, a CSV file with a comment field containing `; rm -rf ~/data`
might not cause SQL injection in the traditional sense, but if Claude reads that file and
passes the content to a shell command without sanitization, the effect is the same.

## What this harness tests

The tests in `test_prompt_injection.py` verify that the pipeline source code does not contain
patterns that would execute or interpret attacker-controlled input:

- **No `eval` or `exec`** — the pipeline should never evaluate strings as code, regardless
  of where those strings come from.
- **No subprocess calls with array data** — reducing or summarizing data should never pass
  array contents to a shell command.
- **No string formatting into shell commands** — f-strings or `%` formatting should not be
  used to construct shell commands from data values.
- **No `pickle.loads` of external data** — pickle deserialization of untrusted data is
  arbitrary code execution.

These tests work by parsing the pipeline source files with Python's `ast` module and walking
the syntax tree to look for dangerous call patterns. They do not call Claude or require any
external services.

## Running the harness

The harness is intentionally excluded from the default `pytest` test collection (see
`pyproject.toml` `testpaths`) to avoid slowing the normal development loop.

Run it explicitly:

```
pytest security/prompt-injection-harness/ -v
```

## Limitations

Static analysis cannot catch all injection risks. These tests check for obvious patterns in
the current source code. They will not catch:

- Dynamic import of code at runtime
- Injection through third-party library internals
- Injection via model output being passed back to the model (second-order injection)

For a comprehensive assessment, also review how Claude is prompted to interact with data
and what tools it has access to during a session involving real data files.
