#!/usr/bin/env python3
"""Verify an audit's output against the lens files, so "done" is checked, not claimed.

Usage:
  verify.py [out=.audit] [--root .] [--lens a,b]

Checks, per findings file (findings/<lens>[-<shard>].md):
  - every finding block has every field of the finding format, with allowed values;
  - its probe exists in the lens, and its `where` path exists in the repo (and the line, when given);
  - a CONFIRMED verdict names a reproduction file that exists under <out> or the repo;
  - every probe of the lens ends in a finding or a `clean:` line (shards of one lens are pooled);
  - conditional probes may close as `clean: <probe> — n/a: <why the condition does not hold>`;
  - every `### ` heading is a finding heading (`### LENS-1 claim`), so a malformed one is not skipped.
And across the audit: the output directory, SCAN.md and at least one findings file exist; every lens
SCAN.md says fires has a findings file; REPORT.md (when present) places every surviving finding id and
comes with refuted.md; no id is both in findings and in refuted.md. Exit 1 on any problem.
This checks the shape and completeness of the output, not whether a finding is true.
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan import load_lenses, read_text  # noqa: E402  the lens files are the single source of probes

FIELDS = ("where", "probe", "scenario", "severity", "detectability", "verdict", "fix family")
SEVERITY = {"critical", "high", "medium", "low"}
DETECTABILITY = {"loud", "quiet", "silent"}
HEADING = re.compile(r"^### ([A-Z]+-\d+) (.+)$", re.MULTILINE)
FIELD = re.compile(r"^- ([a-z ]+): (.+)$", re.MULTILINE)
CLEAN = re.compile(r"^clean: ([a-z0-9-]+) [—-]+ (.+)$", re.MULTILINE)
FIRES = re.compile(r"^- \*\*([a-z]+)\*\* fires", re.MULTILINE)


def parse(text):
    """(findings, clean lines) from one findings file. A finding is a heading plus its field lines."""
    findings = []
    starts = [m.start() for m in HEADING.finditer(text)] + [len(text)]
    for start, end in zip(starts, starts[1:]):
        block = text[start:end]
        head = HEADING.match(block)
        findings.append(dict(id=head.group(1), claim=head.group(2),
                             **{k: v.strip() for k, v in FIELD.findall(block) if v.strip()}))
    malformed = [line for line in text.splitlines() if line.startswith("### ") and not HEADING.match(line)]
    return findings, dict(CLEAN.findall(text)), malformed


def check_finding(f, lens, root, out):
    problems = [f"missing field '{k}'" for k in FIELDS if k not in f]
    if f.get("severity", "").split()[0:1] and f["severity"].split()[0] not in SEVERITY:
        problems.append(f"severity '{f['severity']}' is not one of {sorted(SEVERITY)}")
    if f.get("detectability", "").split()[0:1] and f["detectability"].split()[0] not in DETECTABILITY:
        problems.append(f"detectability '{f['detectability']}' is not one of {sorted(DETECTABILITY)}")
    verdict = f.get("verdict", "")
    if verdict and not re.match(r"(CONFIRMED|PLAUSIBLE)\b", verdict):
        problems.append(f"verdict '{verdict}' is not CONFIRMED or PLAUSIBLE")
    if verdict.startswith("CONFIRMED") and not names_existing_file(verdict[len("CONFIRMED"):], (out, root)):
        problems.append("CONFIRMED verdict names no reproduction file that exists under the output or the repo")
    if "probe" in f and f["probe"] not in lens.probes:
        problems.append(f"probe '{f['probe']}' is not in lenses/{lens.name}.md")
    if "where" in f:
        problems += check_where(f["where"], root)
    return problems


def inside(base, path):
    """The real path of `path` under `base`, or None when it resolves outside (absolute paths, `..`, symlinks)."""
    base, full = os.path.realpath(base), os.path.realpath(os.path.join(base, path))
    return full if full.startswith(base + os.sep) else None


def names_existing_file(text, bases):
    """True when a word of `text` (backticks, brackets and a trailing :line dropped) is a file under one of `bases`."""
    for word in re.split(r"[\s,;()`]+", text):
        word = re.sub(r":\d+$", "", word)
        if word and any(os.path.isfile(inside(base, word) or "") for base in bases):
            return True
    return False


def check_where(where, root):
    # the whole value first, so a path with spaces works; then its first word, so trailing notes are allowed
    for candidate in (where.strip("` "), where.split()[0].strip("`")):
        m = re.match(r"(.+?)(?::(\d+))?$", candidate)
        path, line = m.group(1), m.group(2)
        full = inside(root, path)
        if full and os.path.isfile(full):
            break
    else:
        if not inside(root, path):
            return [f"where path '{path}' is outside the repo"]
        return [f"where path '{path}' does not exist"]
    if line and int(line) > len(read_text(full).splitlines()):
        return [f"where line {line} is past the end of {path}"]
    return []


def verify(out, root, only):
    lenses = load_lenses()
    problems, ids, counts = [], [], collections.Counter()
    if not os.path.isdir(out):
        return [f"{out}: no such output directory, so no audit ran"], ids, counts, set()
    covered = collections.defaultdict(set)
    files = sorted(os.listdir(os.path.join(out, "findings"))) if os.path.isdir(os.path.join(out, "findings")) else []
    seen_lenses = set()
    for name in files:
        if not name.endswith(".md"):
            continue
        lens_name = name[:-3].split("-")[0]
        if only and lens_name not in only:
            continue
        lens = lenses.get(lens_name)
        if not lens:
            problems.append(f"findings/{name}: no lens named '{lens_name}'")
            continue
        seen_lenses.add(lens_name)
        findings, clean, malformed = parse(read_text(os.path.join(out, "findings", name)))
        problems += [f"findings/{name}: heading '{line}' is not '### LENS-1 claim', so its block was not checked"
                     for line in malformed]
        for f in findings:
            problems += [f"findings/{name} {f['id']}: {p}" for p in check_finding(f, lens, root, out)]
            covered[lens_name].add(f.get("probe"))
            ids.append(f["id"])
            counts[f.get("severity", "?").split()[0]] += 1  # parse() drops blank values, so this is never empty
        for probe, evidence in clean.items():
            if probe not in lens.probes:
                problems.append(f"findings/{name}: clean line names unknown probe '{probe}'")
            elif evidence.lower().startswith("n/a") and probe not in lens.conditional:
                problems.append(f"findings/{name}: '{probe}' is unconditional, so n/a cannot close it")
            covered[lens_name].add(probe)
    for lens_name in seen_lenses:
        missing = [p for p in lenses[lens_name].probes if p not in covered[lens_name]]
        problems += [f"lens {lens_name}: probe '{p}' has no finding and no clean line" for p in missing]

    if not seen_lenses:
        problems.append("no findings file was checked" + (f" for {', '.join(sorted(only))}" if only else ""))
    scan_md = os.path.join(out, "SCAN.md")
    if os.path.isfile(scan_md):
        fired = set(FIRES.findall(read_text(scan_md)))
        problems += [f"lens {l} fires in SCAN.md but has no findings file" for l in sorted(fired - seen_lenses)
                     if not only or l in only]
    else:
        problems.append("SCAN.md is missing, so the lenses that should have findings are unknown")

    def mentions(text, i):  # LENS-1 must not match inside LENS-10
        return re.search(rf"(?<![\w-]){re.escape(i)}(?!\d)", text)

    report_md, refuted_md = os.path.join(out, "REPORT.md"), os.path.join(out, "refuted.md")
    refuted = read_text(refuted_md) if os.path.isfile(refuted_md) else None
    if os.path.isfile(report_md) and not only:
        report = read_text(report_md)
        problems += [f"REPORT.md does not place {i}" for i in ids if not mentions(report, i)]
        if refuted is None:
            problems.append("REPORT.md exists but refuted.md does not; write it, with `none` when nothing was refuted")
    if refuted and not only:
        problems += [f"{i} is in refuted.md and still in findings; a refuted finding is removed from findings"
                     for i in ids if mentions(refuted, i)]
    duplicates = [i for i, n in collections.Counter(ids).items() if n > 1]
    problems += [f"finding id {i} appears more than once; merge with an `also:` line" for i in duplicates]
    return problems, ids, counts, seen_lenses


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=".audit")
    ap.add_argument("--root", default=".", help="the audited repo, for checking `where` paths")
    ap.add_argument("--lens", help="verify only these lenses (a hunter checking its own file)")
    a = ap.parse_args()
    only = set(a.lens.split(",")) if a.lens else None
    problems, ids, counts, lenses = verify(a.out, os.path.abspath(a.root), only)
    if problems:
        print("\n".join(problems))
        print(f"\nnot verified: {len(problems)} problems")
        return 1
    by_sev = ", ".join(f"{counts[s]} {s}" for s in ("critical", "high", "medium", "low") if counts[s])
    print(f"verified: {len(ids)} findings ({by_sev or 'none'}) across {len(lenses)} lenses, every probe answered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
