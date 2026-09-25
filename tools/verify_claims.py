#!/usr/bin/env python3
"""Verify that every figure asserted in README.md still matches the committed catalogue.

The README quotes counts, sizes, hashes and line numbers taken from
`references/deepseek-4.1-flash-mappings.txt`. Those claims go stale the moment
anyone touches the catalogue, and a stale number in a research document is worse
than no number. Run this after changing either file:

    python tools/verify_claims.py

Exit status 0 means every claim holds. Exit status 1 means the README and the
data disagree, and it prints which claim failed. Nothing here writes to any file.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogue import parse, DEFAULT_PATH  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
README = REPO / "README.md"

# --- figures the README asserts -------------------------------------------
EXPECTED = {
    "categories": 12,
    "mapping_lines": 266,
    "term_instances": 781,
    "distinct_terms": 779,
    "single_word_terms": 424,
    "multiword_terms": 355,
    "distinct_substitutes": 246,
    "declared_total": 271,
    "lines_with_one_variant": 79,
    "max_variants": 17,
}

# category -> (declared, mapping lines, term instances, distinct terms)
PER_CATEGORY = {
    "general":              (118, 118, 316, 315),
    "cyber":                (68, 68, 156, 156),
    "mature-content":       (41, 36, 114, 113),
    "model-control":        (13, 13, 45, 45),
    "weapons":              (7, 7, 29, 29),
    "privacy":              (6, 6, 16, 16),
    "severe-harm":          (6, 6, 45, 45),
    "hate-abuse":           (4, 4, 27, 27),
    "controlled-substance": (3, 3, 12, 12),
    "fraud":                (3, 3, 15, 15),
    "civic-information":    (1, 1, 3, 3),
    "restricted-content":   (1, 1, 3, 3),
}

DUPLICATE_TERMS = {"ejaculation": [5, 12], "sexual blackmail": [214, 215]}
ANNOTATED_LINES = [209, 212]

# widest mapping lines the README names, as (line, category, variants)
WIDEST = [(266, "severe-harm", 17), (62, "general", 12), (76, "general", 12),
          (237, "model-control", 12), (270, "hate-abuse", 12)]

# Byte-level identity of the file as committed (CRLF in the working tree, LF in git).
SIZES = {"crlf_bytes": 19945, "lf_bytes": 19657, "lines": 289, "terminated": 288}
SHA256 = {"crlf": "cda8b243d2d9381e710865d74f2084e038ab23385fe88941a0f3b83c9e56758d",
          "lf":   "226eab20b6fc47bd6bb6a8303a1cd4fb6a9ca428f209c8b42e0b6d7ad39c200e"}
BLOB = "5766fd05b70b7b7a9eca5a659d0e7a89f604fdcf"

# Strings the README must contain, so the prose cannot drift away from the data
# it claims to summarise.
README_MUST_CONTAIN = [
    "**266**", "**779**", "**246**", "217 of 266", "60.5%", "86.5%", "7.50",
    "17 surface forms on one line", "L266", "blob `5766fd05",
    "lines 5 and 12", "lines 214 and 215", "references/CHANGELOG.md",
]

# Guard: the excised minor-related entries must not come back. Deliberately kept
# to short markers so this checker does not itself republish the excised vocabulary.
EXCISED_MARKERS = ("csam", "csem", "csae", "csai", "underage")


def main():
    cat = parse(DEFAULT_PATH)
    fig = cat.figures()
    raw = DEFAULT_PATH.open("rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    readme = README.read_text(encoding="utf-8")

    checks = []

    for key, want in EXPECTED.items():
        got = fig[key]
        checks.append(("figure %s == %s" % (key, want), got == want, got))

    for name, (decl, lines, instances, distinct) in PER_CATEGORY.items():
        d = fig["per_category"].get(name)
        got = None if d is None else (d["declared"], d["mapping_lines"],
                                      d["term_instances"], d["distinct_terms"])
        checks.append(("category %s == %s" % (name, (decl, lines, instances, distinct)),
                       got == (decl, lines, instances, distinct), got))

    checks.append(("duplicate terms == %s" % DUPLICATE_TERMS,
                   fig["duplicate_terms"] == DUPLICATE_TERMS, fig["duplicate_terms"]))
    checks.append(("annotated lines == %s" % ANNOTATED_LINES,
                   fig["annotated_lines"] == ANNOTATED_LINES, fig["annotated_lines"]))

    for line, catname, variants in WIDEST:
        r = next((r for r in cat.rows if r.line == line), None)
        got = None if r is None else (r.line, r.category, r.variant_count)
        checks.append(("widest line L%d = %s x%d" % (line, catname, variants),
                       got == (line, catname, variants), got))

    # byte-level identity
    got = {"crlf_bytes": len(raw), "lf_bytes": len(lf),
           "lines": len(raw.decode("utf-8").split("\n")),
           "terminated": raw.count(b"\r\n")}
    checks.append(("file byte sizes == %s" % SIZES, got == SIZES, got))
    checks.append(("sha256 crlf == %s.." % SHA256["crlf"][:12],
                   hashlib.sha256(raw).hexdigest() == SHA256["crlf"],
                   hashlib.sha256(raw).hexdigest()[:12]))
    checks.append(("sha256 lf == %s.." % SHA256["lf"][:12],
                   hashlib.sha256(lf).hexdigest() == SHA256["lf"],
                   hashlib.sha256(lf).hexdigest()[:12]))

    # README consistency
    for s in README_MUST_CONTAIN:
        checks.append(("README contains %r" % s, s in readme, "present" if s in readme else "MISSING"))
    checks.append(("README names this script",
                   "tools/verify_claims.py" in readme, "present" if "tools/verify_claims.py" in readme else "MISSING"))
    checks.append(("README names the blob %s.." % BLOB[:8], BLOB in readme,
                   "present" if BLOB in readme else "MISSING"))

    # excision guard
    low = raw.decode("utf-8", "replace").lower()
    for marker in EXCISED_MARKERS:
        checks.append(("excised marker %r absent" % marker, marker not in low,
                       "absent" if marker not in low else "PRESENT"))

    failed = [(n, got) for n, ok, got in checks if not ok]
    for name, ok, got in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", name))
    print("\n%d/%d checks pass" % (len(checks) - len(failed), len(checks)))
    if failed:
        print("\nfailed:")
        for name, got in failed:
            print("  %s   (got: %r)" % (name, got))
        return 1
    print("every figure in README.md matches the committed catalogue")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
