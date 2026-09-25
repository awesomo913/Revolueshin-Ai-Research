# references/ changelog

Changes to the files in this folder. The catalogue is source data and is not edited in place except
where the repo owner directs an excision. Those are recorded here so a change to the vocabulary is
visible rather than silent.

## 2026-09-24 — excision from `deepseek-4.1-flash-mappings.txt`

Three mapping lines were removed from the `mature-content` category at the owner's direction: the
entries concerning minor-related material, which were lines 218–220 of the previous revision.

| | Before | After |
| --- | --- | --- |
| Bytes (working tree, CRLF) | 20,314 | 19,945 |
| File lines | 292 | 289 |
| Mapping lines | 269 | 266 |
| `mature-content` mapping lines | 39 | 36 |
| Distinct raw terms | 794 | 779 |
| git blob | (removed from history) | `5766fd05b70b7b7a9eca5a659d0e7a89f604fdcf` |

**The removed terms are not reproduced in this changelog, or anywhere else in this repository.**
The prior revision was withdrawn rather than deprecated: this repository's history was rebuilt on
2026-09-24 so that no reachable revision contains the excised entries. No commit, blob or tree here
holds them, and the pre-excision blob hashes are dead — do not cite them. Any figure taken from a
revision with 269 mapping lines and 794 distinct terms refers to content that no longer exists in
this repository, and its counts are reported below only so the two revisions can be told apart.

This repository has a single commit as a result of that rebuild. Anything relying on figures from
the previous revision needs re-deriving. `tools/verify_claims.py`
holds the current values and will fail loudly against stale ones.

Two minor-related entries outside `mature-content` were left in place at the time of this excision
(`age play` in `general`, and `grooming` in `general`) and were flagged to the owner for a decision.
