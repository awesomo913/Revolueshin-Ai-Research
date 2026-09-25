#!/usr/bin/env python3
"""Parse and query the DeepSeek 4.1 Flash detection-vocabulary catalogue.

The catalogue is a flat text file of the form:

    [category-name N]
    term / alternate term / third term -> neutral substitute

This module is the single parser for that format. Anything else in this repo that
needs figures from the catalogue imports this rather than re-implementing the
split, so the two traps documented in the README -- that splitting on '->' must be
limited to one split, and that the '/' separated terms must be whitespace-stripped
-- are handled in exactly one place.

Usage:
    python tools/catalogue.py summary
    python tools/catalogue.py categories
    python tools/catalogue.py category NAME
    python tools/catalogue.py find TERM
    python tools/catalogue.py search SUBSTRING
    python tools/catalogue.py widest
    python tools/catalogue.py check
    python tools/catalogue.py json [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_PATH = REPO / "references" / "deepseek-4.1-flash-mappings.txt"

# Category headers look like "[general 118]". The file opens with one of these,
# which is why file(1) misreports the whole thing as a Generic INItialization
# configuration -- it sees a bracket-shaped section list.
HEADER_RE = re.compile(r"^\[([a-z\- ]+)\s+(\d+)\]$")


class Row:
    """One mapping line: N surface forms on the left, one substitute on the right."""

    __slots__ = ("line", "category", "terms", "substitute")

    def __init__(self, line, category, terms, substitute):
        self.line = line
        self.category = category
        self.terms = tuple(terms)
        self.substitute = substitute

    @property
    def variant_count(self):
        return len(self.terms)

    def as_dict(self):
        return {
            "line": self.line,
            "category": self.category,
            "terms": list(self.terms),
            "substitute": self.substitute,
            "variant_count": self.variant_count,
        }


class Catalogue:
    """A parsed catalogue: rows, the counts the headers claim, and derived figures."""

    def __init__(self, rows, declared, order, path):
        self.rows = rows
        self.declared = declared        # category -> the number its header claims
        self.order = order              # categories, in file order
        self.path = str(path)

    # --- accessors -------------------------------------------------------
    @property
    def by_category(self):
        out = {name: [] for name in self.order}
        for r in self.rows:
            out[r.category].append(r)
        return out

    def terms(self):
        for r in self.rows:
            for t in r.terms:
                yield t

    def distinct_terms(self):
        return set(self.terms())

    def find(self, term):
        """Exact (case-insensitive) match on a raw term."""
        key = term.strip().lower()
        return [r for r in self.rows if any(t.lower() == key for t in r.terms)]

    def search(self, substring):
        """Case-insensitive substring match across raw terms."""
        key = substring.strip().lower()
        return [r for r in self.rows if any(key in t.lower() for t in r.terms)]

    def duplicate_terms(self):
        """Raw terms appearing on more than one line -> {term: [line, ...]}."""
        seen = {}
        for r in self.rows:
            for t in r.terms:
                seen.setdefault(t, []).append(r.line)
        return {t: lines for t, lines in seen.items() if len(lines) > 1}

    def annotated_lines(self):
        """Lines the catalogue itself flags with an inline '[appears twice' note.

        Read from the raw text because the note sits after the substitute and is
        not part of a parsed Row.
        """
        text = Path(self.path).read_text(encoding="utf-8", errors="replace")
        return [i for i, ln in enumerate(text.splitlines(), 1) if "appears twice" in ln]

    def widest(self, n=10):
        return sorted(self.rows, key=lambda r: -r.variant_count)[:n]

    # --- figures ---------------------------------------------------------
    def figures(self):
        by_cat = self.by_category
        terms = list(self.terms())
        distinct = set(terms)
        fig = {
            "categories": len(self.order),
            "mapping_lines": len(self.rows),
            "term_instances": len(terms),
            "distinct_terms": len(distinct),
            "single_word_terms": sum(1 for t in distinct if " " not in t),
            "multiword_terms": sum(1 for t in distinct if " " in t),
            "distinct_substitutes": len({r.substitute for r in self.rows}),
            "declared_total": sum(self.declared.values()),
            "lines_with_one_variant": sum(1 for r in self.rows if r.variant_count == 1),
            "max_variants": max(r.variant_count for r in self.rows),
            "duplicate_terms": self.duplicate_terms(),
            "annotated_lines": self.annotated_lines(),
            "variant_distribution": {},
            "per_category": {},
            "widest_lines": [
                {"line": r.line, "category": r.category,
                 "variant_count": r.variant_count, "substitute": r.substitute}
                for r in self.widest()
            ],
        }
        for r in self.rows:
            k = r.variant_count
            fig["variant_distribution"][k] = fig["variant_distribution"].get(k, 0) + 1
        for name in self.order:
            rs = by_cat[name]
            fig["per_category"][name] = {
                "declared": self.declared[name],
                "mapping_lines": len(rs),
                "term_instances": sum(r.variant_count for r in rs),
                "distinct_terms": len({t for r in rs for t in r.terms}),
                "terms_per_line": round(sum(r.variant_count for r in rs) / len(rs), 2) if rs else 0.0,
            }
        return fig

    # --- output ----------------------------------------------------------
    def json_dump(self, out=None):
        payload = {"source": self.path, "figures": self.figures(),
                   "rows": [r.as_dict() for r in self.rows]}
        text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False)
        if out:
            dest = Path(out)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text + "\n", encoding="utf-8")
            return out
        return text


def parse(path=DEFAULT_PATH):
    """Parse the catalogue. The only place the file format is interpreted."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    rows, declared, order, current = [], {}, [], None
    for lineno, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if not stripped:
            continue
        m = HEADER_RE.match(stripped)
        if m:
            current = m.group(1)
            declared[current] = int(m.group(2))
            if current not in order:
                order.append(current)
            continue
        if "->" not in stripped:
            continue
        if current is None:
            raise ValueError("mapping at line %d appears before any category header" % lineno)
        left, substitute = stripped.split("->", 1)      # ONE split, deliberately
        terms = [t.strip() for t in left.split("/") if t.strip()]
        if not terms:
            raise ValueError("line %d has nothing on the left of '->'" % lineno)
        rows.append(Row(lineno, current, terms, substitute.strip()))
    if not rows:
        raise ValueError("no mapping lines found in %s" % path)
    return Catalogue(rows, declared, order, path)


def _fmt_row(row):
    return "%-22s %8d %8d %8d %10s" % (
        row["_name"], row["declared"], row["mapping_lines"],
        row["term_instances"], row["terms_per_line"])


def cmd_summary(cat: Catalogue) -> None:
    fig = cat.figures()
    print("%-22s %8s %8s %8s %10s" % ("category", "declared", "lines", "terms", "terms/line"))
    for name in cat.order:
        d = dict(fig["per_category"][name]); d["_name"] = name
        print(_fmt_row(d))
    print("%-22s %8d %8d %8d" % ("TOTAL", fig["declared_total"], fig["mapping_lines"],
                                 fig["term_instances"]))
    print()
    print("distinct raw terms      :", fig["distinct_terms"])
    print("distinct substitutes    :", fig["distinct_substitutes"])
    print("single-word / multiword : %d / %d" % (fig["single_word_terms"], fig["multiword_terms"]))
    print("lines with one variant  :", fig["lines_with_one_variant"])
    print("widest mapping          : %d variants (line %d)" % (
        fig["max_variants"], max(cat.rows, key=lambda r: r.variant_count).line))


def cmd_check(cat: Catalogue) -> int:
    fig = cat.figures()
    print("structural checks")
    problems = []
    for name in cat.order:
        d = fig["per_category"][name]
        if d["declared"] != d["mapping_lines"]:
            problems.append(name)
            print("  header mismatch  %-22s declares %d, body has %d (differs by %d)" % (
                name, d["declared"], d["mapping_lines"], d["declared"] - d["mapping_lines"]))
    if not problems:
        print("  every category header matches its body")
    n_terms = len(cat.distinct_terms())
    print("\n  rows parsed              : %d" % fig["mapping_lines"])
    print("  term instances           : %d" % fig["term_instances"])
    print("  distinct raw terms       : %d" % n_terms)
    print("  instances not distinct   : %d" % (fig["term_instances"] - n_terms))
    print("  duplicate raw terms      : %s" % (fig["duplicate_terms"] or "none"))
    print("  annotated '[appears twice' lines: %s" % (fig["annotated_lines"] or "none"))
    print("\nnote: header/body mismatches are reported, not treated as failures -- the")
    print("      catalogue is source data and is committed as it stands.")
    return 0


def cmd_print_rows(rows, cat: Catalogue) -> int:
    if not rows:
        print("no match")
        return 1
    for r in rows:
        print("L%-5d %-20s %s" % (r.line, r.category, " / ".join(r.terms)))
        print("      -> %s   [%d variant(s)]" % (r.substitute, r.variant_count))
    print("\n%d row(s)" % len(rows))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["summary", "categories", "category", "find",
                                        "search", "widest", "check", "json"])
    ap.add_argument("argument", nargs="?")
    ap.add_argument("--path", default=str(DEFAULT_PATH))
    ap.add_argument("--out", default=None, help="write JSON here instead of stdout")
    args = ap.parse_args(argv)

    cat = parse(args.path)

    if args.command == "summary":
        cmd_summary(cat)
    elif args.command == "categories":
        for name in cat.order:
            print("%-22s declared %3d  lines %3d" % (
                name, cat.declared[name], len(cat.by_category[name])))
    elif args.command == "category":
        if not args.argument:
            ap.error("category requires a name; try: catalogue.py categories")
        if args.argument not in cat.declared:
            print("unknown category %r. known: %s" % (args.argument, ", ".join(cat.order)))
            return 2
        return cmd_print_rows(cat.by_category[args.argument], cat)
    elif args.command == "find":
        if not args.argument:
            ap.error("find requires a term")
        return cmd_print_rows(cat.find(args.argument), cat)
    elif args.command == "search":
        if not args.argument:
            ap.error("search requires a substring")
        return cmd_print_rows(cat.search(args.argument), cat)
    elif args.command == "widest":
        return cmd_print_rows(cat.widest(int(args.argument) if args.argument else 10), cat)
    elif args.command == "check":
        return cmd_check(cat)
    elif args.command == "json":
        result = cat.json_dump(args.out)
        print("wrote %s" % result if args.out else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
