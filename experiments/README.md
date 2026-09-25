# Experiments

One directory per experiment. Copy the shape below.

```
experiments/YYYY-MM-DD-short-slug/
  README.md      # Question / Method / Result / Reading
  run.py         # reproduces results.json from scratch
  results.json   # raw output, committed
```

Rules that keep this directory useful:

- The directory name starts with the date the experiment was **run**, not planned.
- `run.py` must work from a clean checkout with no manual steps beyond its documented deps.
- `results.json` is the raw record. Never edit it after the fact — re-run and commit the new one.
- If a run failed, commit the failure and its exact error message.
- If it was run by an automated agent rather than by hand, say so in the README.

First experiment is not yet written.
