# ReVo Lue Shin — AI Research

**A frontier model's output filter is invisible.** You cannot read it, you cannot query it, and you
find out what is in it only when something you wrote comes back empty and you have to guess why.

This repository holds the opposite of that: **a written-down detection vocabulary for DeepSeek 4.1
Flash** — 779 terms its detection layer keys on, across 12 categories, each paired with a neutral
substitute. Extracted by probing the model directly. Not a guess, not a scrape of somebody else's
list, not a summary of one. The raw record of the work, committed in full and byte-verified, with a
script that checks every number in this document against it.

Everything else here exists to make measurements like it repeatable, and to turn a word list into
things that can be checked: rates, diffs, time series, comparisons across models.

---

## At a glance

| | |
| --- | --- |
| Categories | **12** |
| Mapping lines | **266** |
| Distinct raw terms | **779** |
| Distinct substitute phrasings | **246** |
| Held in the two largest categories | **60.5%** of all terms (`general` + `cyber`) |
| Lines that are *not* adult-themed | **217 of 266 (82%)** |
| Densest category | `severe-harm`, **7.50** surface forms per line |
| Largest single mapping | `severe-harm`, **17 surface forms on one line** |
| Snapshot metadata | **none — no date, no model build string** |

That last row is the most important one in the table, and it is a problem. See *Prospects*, item 1.

Every figure above is reproducible: `python tools/verify_claims.py` recomputes all of them from the
committed catalogue and fails if this document and the data disagree.

## What lives here

| Path | Contents |
| --- | --- |
| `experiments/` | One directory per experiment. Each one runs end-to-end on its own. |
| `notes/` | Reading notes, model observations, prompt diffs, decision records. |
| `tools/` | Parsers and checkers. Anything reusable, so a number is a script output, not a memory. |
| `data/` | Small inputs and captured outputs (JSON/CSV). Large artifacts are linked, not committed. |
| `references/` | Source data. Not edited in place except by a recorded excision — see `references/CHANGELOG.md`. |
| `archive/` | Retired work, kept for provenance. |

`references/`, `experiments/` and `tools/` exist so far. The rest are commitments, not directories.

## The catalogue

**`references/deepseek-4.1-flash-mappings.txt`** — the vocabulary reference for this repo: the terms
DeepSeek 4.1 Flash's detection layer responds to, each paired with a neutral substitute. Derived by
the repo owner through direct probing of the model to establish which keywords it detects.

The file is the recorded output of that work, not a summary of it. It is kept here so the probing
does not have to be repeated, and so any conclusion drawn from it can be checked against the raw
record. **Scope: research only.** This is a measurement of what gets detected — a description of the
detector, not a bypass for it. Anything built on top of it belongs in `tools/` and cites this file.

The file is not edited in place. A revised vocabulary is a new dated file in `references/`, leaving
the original intact so the two can be diffed and the change can be *seen* rather than asserted. The
one exception is an owner-directed excision, which is recorded in `references/CHANGELOG.md` rather
than made silently. There has been one such excision; it is why the figures here are lower
than those of the withdrawn revision.

## What the catalogue contains

| Category | Declared | Mapping lines | Raw terms | Terms/line |
| --- | --- | --- | --- | --- |
| `general` | 118 | 118 | 316 | 2.68 |
| `cyber` | 68 | 68 | 156 | 2.29 |
| `mature-content` | 41 | 36 | 114 | 3.17 |
| `model-control` | 13 | 13 | 45 | 3.46 |
| `weapons` | 7 | 7 | 29 | 4.14 |
| `privacy` | 6 | 6 | 16 | 2.67 |
| `severe-harm` | 6 | 6 | 45 | 7.50 |
| `hate-abuse` | 4 | 4 | 27 | 6.75 |
| `controlled-substance` | 3 | 3 | 12 | 4.00 |
| `fraud` | 3 | 3 | 15 | 5.00 |
| `civic-information` | 1 | 1 | 3 | 3.00 |
| `restricted-content` | 1 | 1 | 3 | 3.00 |
| **Total** | **271** | **266** | **781** | — |

779 of the 781 are distinct; 424 are single words, 355 are multiword phrases.

## What the numbers already say

Five things fall out of the file itself. All of them are recomputed from the committed file by
`tools/verify_claims.py`, not remembered.

**1. This is not a prudishness filter. It is overwhelmingly a security-and-harm vocabulary.**
217 of the 266 mapping lines — 82% — are not adult/intimacy-themed. Even `general`, the one category
that mixes subjects, is only 18 adult-themed lines out of 118 (15%); the other 100 are security-
operational material (cracking, exfiltration, lateral movement, privilege escalation, supply chain,
log tampering). The intuition that these filters mostly police sex is wrong by more than a factor of
four on this evidence.

**2. The detection weight is concentrated where the surface forms are.** The five largest categories
carry 86.5% of the vocabulary, and `general` + `cyber` alone carry 60.5%. But raw size is not where
the interesting signal is: `severe-harm` has one of the smallest line counts in the file (6) and the
highest density of surface forms (7.50 per line), while `cyber` is the second largest category and
has the *lowest* density (2.29). Severe categories get many spellings and one line each; broad
technical categories get one spelling each and many lines.

**3. Coverage is wildly uneven, and that is a measurement in itself.** 79 of the 266 lines (30%)
carry exactly one surface form — a single spelling the detector must catch. At the other end, the
single 17-variant line is `severe-harm` (L266: the murder/homicide/assassination family), followed by
four 12-variant lines: outbound data transfer (L62), prohibited-conduct subject (L76),
instruction-priority conflict (L237), and identity-targeted abuse (L270). Those five lines are the
detector's highest-investment concepts by spelling count.

**4. The file's own annotations disagree with its own arithmetic.** The category headers declare 271
entries; the file holds 266 mapping lines. The entire gap of 5 is in `mature-content` (41 declared,
36 present), while every other category's header matches its body exactly. Three of those five are
the recorded excision. The remaining two are consistent with the two lines — 209 and 212 — that carry
an inline note reading `[appears twice in the catalogue]`: the header counts entries the body
collapsed. That second half is an inference from the numbers, not a statement the file makes.

**5. And those annotations do not point at the duplicates.** Mechanically, exactly two term strings
appear on more than one line: `ejaculation` (lines 5 and 12) and `sexual blackmail` (lines 214 and 215). Neither carries a note, and neither annotated line (209, 212) contains a repeating string. So
the annotation and a string-level duplicate check are measuring two different things — most likely
topic-level overlap versus literal repetition. **A reviewer has to decide which one they mean before
either number is quoted.** This README reports both and privileges neither.

## Prospects — where this goes

The list below is the reason this repository exists rather than a gist. One of the eight is built
(item 7); the rest are not, and each says what it depends on.

**1. Give the snapshot a header — do this first.**
The file carries *no date and no model build string* (verified: zero matches for a date-like pattern,
`\bversion\b`, or `\bbuild\b` in the whole file). A vocabulary with no vintage cannot join a time
series, cannot be compared to anything, and cannot be cited. One header — model, build, capture date,
probe method — converts a standalone word list into the first point on a curve. Cheapest, highest-
leverage change available, and everything below depends on it. *Status: not started.*

**2. A probe harness in `tools/`.**
Right now the method is a person and a session. A committed harness makes the measurement repeatable
by anyone, makes every snapshot comparable to the next one, and makes a disagreement about the
vocabulary resolvable by re-running rather than by argument. *Status: not started. Blocks items 3 and 4.*

**3. Longitudinal diffing — watch a filter change instead of discovering it mid-task.**
Re-probe on a schedule, commit each snapshot as a new dated file, diff consecutive ones. The output
is a changelog of what a deployed filter started and stopped caring about: terms added, terms
dropped, categories that grew. That is a capability almost nobody has, and it converts "the model
suddenly refused something it used to accept" from an anecdote into a dated, diffable event.
*Status: not started. Depends on 1 and 2.*

**4. Cross-model comparison — the first side-by-side map of what providers police.**
Run the same probe against other models and commit each vocabulary as a dated snapshot. Diffing them
answers, with counts instead of vibes: which providers' filters are broader, and broader *about
what*. The category taxonomy is already shared, so the comparison is structural rather than
impressionistic. A published category-by-category map across frontier models does not currently
exist in this form. *Status: not started. Depends on 1 and 2.*

**5. False-positive measurement — turn "this tripped the filter" into a number.**
With the vocabulary in hand, run it over corpora that are legitimate by any standard: CVE writeups,
security research, news reporting, legal filings, technical documentation. The deliverable is a
false-positive rate per category — a defensible figure for how often ordinary professional writing
collides with the detector, and which categories collide most. This is the item most likely to be
useful to someone who will never probe a model themselves. *Status: not started. Depends on 1.*

**6. Detection-weight analysis — severity, or frequency?**
Item 2 of the findings above is a real, testable question, not a curiosity: does the detector spend
its surface-form budget on severity (many spellings for the worst things) or on frequency (many
spellings for what it sees most)? The `severe-harm` 7.50 vs `cyber` 2.29 density gap is the first
data point and it points at severity. One model's snapshot cannot settle it. Several models' snapshots
can. *Status: first data point exists; the study does not.*

**7. A queryable index in `tools/` — DONE (first cut).**
779 terms in a flat text file was a document, not a dataset. Two scripts now fix that, and they are
the reason the rest of this document can be trusted:

```bash
python tools/catalogue.py summary          # per-category counts and densities
python tools/catalogue.py find exfiltration  # where a term appears
python tools/catalogue.py search lateral     # substring across all terms
python tools/catalogue.py widest 10          # the highest-coverage lines
python tools/catalogue.py json --out data/catalogue.json
python tools/verify_claims.py              # every figure in this README vs the catalogue
```

`catalogue.py` is now the single parser for the format, so the two traps documented below are handled
in exactly one place. `verify_claims.py` recomputes all 12 figures, all 12 per-category rows, the
duplicate and annotation line numbers, the widest-mapping line numbers, the byte sizes and both
sha256 hashes, then checks the prose in this file still contains the values it claims — and fails
loudly if any of it has drifted. It also guards that the excised entries have not crept back.

*Status: done. Unblocks the reproducibility of everything above.*

**8. The write-up.**
Items 1–6 accumulate into something that does not exist yet: a dated, comparative, counted study of
what different providers' detection layers are actually built to catch, with the raw vocabulary for
each committed alongside the analysis instead of summarised away. That is the endgame this repo is
aiming at. *Status: not started. Depends on 3, 4 and 5.*

## Honest limits

Kept here so that nothing above is read as more than it is.

- **This describes a detector's vocabulary, not the detector.** A term appearing in the list does not
  prove any given sentence containing it gets refused. Context, position, surrounding text, and layers
  other than keyword matching all bear on the outcome, and this file models none of that.
- **Low density is not low priority.** `cyber` has the lowest terms-per-line of any category. That is
  consistent with "many concepts, one spelling each" and does not by itself show the filter cares
  less about it.
- **The vintage is unknown.** No date, no build string. Treat this as a snapshot of unknown date
  against an unknown build, and quote numbers from it accordingly.
- **This is not the original snapshot either.** Three entries were excised on 2026-09-24 at the
  owner's direction, and the repository's history was rebuilt the same day so that no reachable
  revision contains them. Every figure here describes the current revision. Figures from a revision
  with 269 mapping lines and 794 distinct terms describe content no longer retrievable here.
- **A term list is a hypothesis about the filter, not a read of its source.**
- **Counts here are measured from the committed file, including the ones that disagree with each
  other.** Where the file's own labels and its body disagree, both numbers are reported.

## Reproducing the numbers in this file

```bash
python tools/verify_claims.py    # exit 0 = this document matches the data
python tools/catalogue.py summary
```

If this document and the catalogue ever disagree, the catalogue is right and this file is a bug.
That is the point of the checker: a stale number in a research document is worse than no number.

## Identity and line endings

This is the one file in the repo whose bytes changed on the way in. It arrived CRLF; this machine has
`core.autocrlf=true`, so git stored it as LF. A `diff` that ignores line endings reports no
difference at all — the text is intact, and the two columns below are the same file in two states.

| Measured | As received (CRLF) | As stored in git (LF) |
| --- | --- | --- |
| Size | 19,945 bytes | 19,657 bytes |
| Lines | 289 (288 CRLF-terminated) | 289 (288 LF-terminated) |
| sha256 | `cda8b243d2d9381e710865d74f2084e038ab23385fe88941a0f3b83c9e56758d` | `226eab20b6fc47bd6bb6a8303a1cd4fb6a9ca428f209c8b42e0b6d7ad39c200e` |
| git blob | — | `5766fd05b70b7b7a9eca5a659d0e7a89f604fdcf` |

The blob hash is the stable identity of this file: the same in every clone on every platform. A
Windows clone with `core.autocrlf=true` restores the CRLF form and its sha256; a Linux clone gets the
LF form and its sha256. **Quote the blob hash, not a byte count, when referring to this file.**

## Two traps for tooling built against this path

1. **`file(1)` misreports it as a Generic INItialization configuration (INI).** The first line is
   `[general 118]` and every category header is bracket-shaped, so the magic-number check sees an INI
   section list. Do not trust `file` here — read the first line and match the header format
   `^\[[a-z\- ]+ \d+\]$` instead.
2. **The format is one `->` per line, `/`-separated on the left.** Splitting on `->` without limiting
   to one split, or splitting the left side on `/` without stripping whitespace, silently produces
   wrong terms. The 355 multiword terms are where a naive parser loses data.

Both are handled by `tools/catalogue.py`. Use it rather than writing a third parser.

## Structure of an experiment

```
experiments/2026-09-24-temperature-sweep/
  README.md      # question, method, result, what it means
  run.py         # reproduces the result from scratch
  results.json   # the raw output, committed so it is diffable
```

Every experiment README answers four things, in this order:

1. **Question** — what was unknown before this ran.
2. **Method** — model, version, parameters, number of runs, and how it was scored.
3. **Result** — the actual numbers, copied from `results.json`.
4. **Reading** — what it does and does not support. Limits stated explicitly.

## Conventions

- **Raw output is committed.** Summaries are claims; `results.json` is evidence. Both go in.
- **Numbers in a README are copied from a committed file**, never retyped from memory — and where
  possible checked by a script, as `tools/verify_claims.py` does for this one.
- **Negative results stay.** "This did not work" is a result and gets the same four sections.
- **One variable per experiment.** If two things changed, that is two experiments.
- **Failures are recorded with the exact error**, not paraphrased.
- **Anything not actually run is labelled `unverified`** in the note where it appears.
- **Snapshots are not edited** except by an owner-directed excision, which is recorded in
  `references/CHANGELOG.md`. Where the intent is withdrawal rather than curation, the repository
  history is rebuilt as well, so no reachable revision still contains the removed entries.

## Environment

Verified on the machine this repo was set up on:

- Windows 11
- Git, driven from git-bash (POSIX shell) on a Windows host
- `uv` for Python environments
- Python 3.11 / 3.14 available
- `tools/` scripts are stdlib-only and run under either

Each experiment should pin what it needs in its own README. Assume nothing global.

## Running an experiment

```bash
cd experiments/<experiment-name>
uv run python run.py     # or: python run.py
```

## Status

Repository scaffolded 2026-09-24.

- **One reference catalogue committed** — `references/deepseek-4.1-flash-mappings.txt`, 779 distinct
  terms, 12 categories, blob `5766fd05b70b7b7a9eca5a659d0e7a89f604fdcf`. One recorded excision, in
  `references/CHANGELOG.md`.
- **Two tools committed** — `tools/catalogue.py` (the single parser and index) and
  `tools/verify_claims.py` (the claim checker, guarding every figure above).
- **Zero experiments committed.** `experiments/` documents the format for the first one.
- **One of eight prospects built.** Item 7 is done; items 1–6 and 8 are not, and this section stays
  honest about which is which.

## Provenance

Originated by ReVo Lue Shin. The catalogue in `references/` was derived by the owner through direct
probing of DeepSeek 4.1 Flash. Experiments note whether they were run by hand or by an automated
agent, and agent-run results are marked as such.
