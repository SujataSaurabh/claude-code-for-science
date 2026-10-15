# Friction log

Running log of friction moments encountered while developing and using this toolkit.
See `friction-log-template.md` for the entry format.

---

### pytest hook fired on non-test file edit, ran the wrong test file

**Date:** 2026-09-14

**Task:**
Editing `example-pipeline/pipeline/reduce.py` to fix an E501 line-too-long issue flagged
by the ruff hook. The edit was purely cosmetic — splitting a long log.info() call across
multiple lines.

**Expected behavior:**
The ruff hook fires, finds no remaining lint errors, exits 0. No pytest hook activity,
because I did not edit a test file.

**Actual behavior:**
Both hooks fired. The pytest hook matched on `reduce.py` because its filename check
(`if [[ "$BASENAME" != test_*.py && "$BASENAME" != *_test.py ]]; then exit 0; fi`) was
correct, so it should have exited 0 immediately. But I had an earlier draft of the hook
that lacked the filename check and instead ran pytest on any `.py` file, passing the source
file path as the test path. pytest then reported "no tests ran" and exited 5, which the hook
interpreted as a failure and printed to stderr, surfacing a red herring error in the session.

The current hook scripts are correct and include the filename check. The friction was from
the earlier draft and is resolved. Documenting it because it illustrates how easy it is to
get hook exit-code semantics wrong.

**Severity:** medium

**Suggested fix:**
Add an explicit test in the hook development process: run the hook script manually with a
fabricated stdin payload pointing at a non-test `.py` file, and confirm it exits 0 with no
output. This makes the skip path explicit rather than inferred.

**Workaround used:**
Identified the hook was using the wrong exit code (pytest exit 5 = "no tests collected",
not a test failure). Updated the hook to only fire on `test_*.py` and `*_test.py` filenames.
