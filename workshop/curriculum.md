# Workshop Curriculum: Claude Code for Scientific Python Pipelines

90 minutes. Hands-on throughout. No slides-only segments beyond the first 10 minutes.

---

## 0–10 min: Introduction and setup check

**Facilitator actions:**
- Introduce the problem: scientists write a lot of pipeline boilerplate (logging, type hints,
  docstrings, error handling) that is tedious and inconsistently applied
- Introduce the repo and the `sci` plugin: three skills, one reviewer agent, two hooks
- Have everyone confirm setup is working:
  ```
  cd claude-code-for-science
  pytest          # should print 29 passed
  claude --plugin-dir ./plugin
  ```
  In the Claude Code session: type `/sci:standards` and confirm it appears as a suggestion

**Key point to make:** Claude Code is a tool for the agentic loop — generate, lint, test, repeat.
The plugin hooks run ruff and pytest automatically on every file edit. You will see failures
surfaced in the conversation without running them manually.

---

## 10–30 min: /sci:standards — applying coding standards

**Task:** Apply the standards skill to `example-pipeline/pipeline/reduce.py`.

```
/sci:standards example-pipeline/pipeline/reduce.py
```

**What to observe:**
- Claude reads the file, identifies gaps (any missing type hints, bare print calls, etc.)
- Claude makes edits; the ruff hook fires and reports any lint issues
- The result should be a function with complete type annotations and a NumPy-style docstring

**Discussion prompt (5 min):**
- What did Claude do well?
- What would you check before accepting this output in a real project?
- Did it preserve the algorithm correctly? How would you verify that?

**Facilitator note:** Point out that the tests in `example-pipeline/tests/test_reduce.py` provide
a safety net — if Claude changed the behavior, the pytest hook would have flagged it. This is
why tests matter even more when using an AI coding tool.

---

## 30–50 min: /sci:new-flow — scaffolding a new pipeline stage

**Task:** Add a new pipeline stage called `normalize`.

```
/sci:new-flow normalize
```

Claude first asks what the stage should do scientifically. For this exercise, answer briefly
(for example, "scales a 1D intensity curve; leave the implementation as a TODO") so the
participant writes the logic themselves.

**What Claude creates:**
- `example-pipeline/pipeline/normalize.py` — module with a typed, documented function
- `example-pipeline/tests/test_normalize.py` — pytest file with scaffolded test cases

**Participant exercise:**
Edit `normalize.py` to implement a real normalization: divide each bin's intensity by the
maximum intensity to produce a curve on [0, 1]. Then make the scaffolded test pass.

This is intentionally open-ended. Claude can help, but the participant should drive the
implementation and verify the test passes.

**Discussion prompt (5 min):**
- Where did the scaffold save time?
- What did you have to fill in yourself?
- How would you write the test for edge cases (all-zero input, single bin)?

---

## 50–70 min: /sci:review-pipeline — auditing a pipeline

**Task:** Run the pipeline reviewer on the full pipeline directory.

```
/sci:review-pipeline example-pipeline/pipeline/
```

**What the reviewer produces:**
A structured report with:
- Summary paragraph
- Issues found (high / medium / low severity)
- Suggested next steps

**Participant exercise (10 min):**
Read the review output. Pick one medium- or low-severity issue and implement the suggested fix.
Then confirm the tests still pass.

**Discussion prompt (5 min):**
- Was the review accurate? Did it miss anything obvious?
- Did it flag anything that is not actually a problem in your domain?
- How would you use this on your own pipeline code?

---

## 70–85 min: Friction log exercise

**Task:** Fill in one entry of `docs/friction-log-template.md` based on something that did not
work as expected during this workshop.

Examples of valid friction:
- Claude added code you did not ask for
- A hook fired at an unexpected time
- The reviewer flagged something that is correct for your use case
- The scaffold produced something that needed significant editing

**Why this matters:** Friction logs are how this toolkit improves. The template asks for a
suggested fix — even a vague one is useful.

If everything worked smoothly, write about a moment where you were uncertain what would happen
next. That uncertainty is also a signal.

---

## 85–90 min: Debrief

Facilitator-led discussion:

1. What is one thing Claude Code did during this workshop that saved real time?
2. What is one place where you would not trust Claude's output without review?
3. Would you use this on a real pipeline? What would need to be different?

Collect post-surveys before participants leave (see `post-survey.md`).
