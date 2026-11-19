# Self-audit, 2026-11-18

Audited first on a stale local copy (`ed9fdb9`), then re-checked against `main` at `cfa0cf9`. Scope: `skills/audit/scripts/`, `tests/`, the manifests, `README.md` and `AGENTS.md`. The lens files, `DELIVER.md`, `UNTANGLE.md` and the eval cases were skimmed, not probed. This is a hand audit in the skill's finding format, not a full skill run: not every probe was answered, so `verify.py` was not run on it.

On `cfa0cf9`, `scan.py --check` and the unit tests pass on Python 3.12 and on the stock macOS 3.9.6.

## Fundamentals: where each one stands

The statements and their checks live in [README.md](README.md#fundamentals-this-repo-holds-itself-to). Status on `cfa0cf9` plus this branch:

| # | Fundamental | Status |
|---|---|---|
| 1 | One home per fact | Holds: the version lives in `plugin.json`, and a test now ties the other two manifests to it (DESIGN-1). The descriptions differ per listing on purpose |
| 2 | Done is checked, not claimed | Holds: `verify.py` fails on a missing output, on no findings or no `SCAN.md`, and matches report ids by whole word (fixed upstream in PR 9) |
| 3 | Runs where it says it runs | Holds: imports on 3.9; CI runs 3.9 on ubuntu-22.04 and a current Python (PR 11) |
| 4 | Every check runs on every change | Holds except for the eval suite, which needs an API key and stays manual |
| 5 | A test goes red on the regression it guards | Holds for every finding below: each new test failed before its fix |
| 6 | Parse at the edge, fail loud | Holds: bad TSV rows and regexes exit with `file:line`; bad arguments exit 2 |
| 7 | Scope is what it claims | Holds: `--since` covers staged, unstaged, untracked, spaced and subfolder paths (PR 10) |
| 8 | Cost grows with the input, not its square | Fixed here: `--since` diffed once per file, now once per scan (PERFORMANCE-1) |
| 9 | Read-only until approved | Holds by instruction; the `resume-unapproved` eval and its fixture test check it |
| 10 | Docs match the code | Fixed here: marketplace text and the usage note (DESIGN-2) |

## Fixed upstream before this branch

The first pass on the stale copy also found these, and `main` had already fixed them: scripts crashing on Python 3.9; `verify.py` passing on a missing output; report ids matched as substrings; `--since` missing staged and untracked files; no CI; unanchored dependency patterns firing the money and data lenses.

## Findings fixed on this branch

### PERFORMANCE-1 --since runs git per file
- where: skills/audit/scripts/scan.py:442
- probe: quadratic
- scenario: `--since` on a 20,000-file monorepo → `changed_since()` sits in the list comprehension's condition, so it runs three `git` commands for every tracked file before the scan starts
- severity: medium
- detectability: quiet
- verdict: CONFIRMED (`test_since_diffs_once_per_scan` saw 3 calls on a 3-file repo; 63 on this repo)
- fix family: hoist the call out of the loop

### DESIGN-1 version copied across three manifests, nothing ties them
- where: .claude-plugin/plugin.json:3
- probe: copies
- scenario: the next release bumps `plugin.json` only → marketplace and Gemini listings show the old version
- severity: low
- detectability: quiet
- verdict: PLAUSIBLE
- fix family: one source and a test that the copies agree (`test_manifests_share_one_version`)

### DESIGN-2 docs drift in marketplace text and usage
- where: .claude-plugin/marketplace.json:7
- probe: docs-drift
- scenario: a reader of the listing sees "audit and one-pass untangle skills" for what is one skill; the README usage table omits `--fix` and `--out`, which `SKILL.md`'s argument hint lists
- severity: low
- detectability: quiet
- verdict: CONFIRMED (read both files against `skills/audit/SKILL.md`)
- fix family: keep flags in one place and point to it

## Not covered

Eleven lens files were not probed, `DELIVER.md` and `UNTANGLE.md` were read only in part, the eval graders were not read, and the eval suite was not run.
