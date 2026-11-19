# Self-audit, 2026-11-19

A full run of the skill on itself at `0331db4`: scan, recon, the eight lenses that fired (design, failure, operations, performance, security, state, tests, types) in sequence, a refutation pass, and a report on which `verify.py` passes (21 surviving findings: 7 medium, 14 low; 1 refuted). No subagents were available, so the refutation was a second pass by the same model, which is weaker evidence than a separate refuter. `SKILL.md`, the lens files, `DELIVER.md` and `UNTANGLE.md` were read and probed but not changed, because a change there needs the eval suite and the suite was not run. vulture and gitleaks are not installed, so neither ran, and the clone held one commit, so `cochange.sh` had no history to pair.

After this branch: `scan.py --check` passes, 88 unit tests pass on Python 3.13 and 3.9, and `claude plugin validate .` passes with its icon warning.

## Fixed on this branch

Each has a test that was red before its fix.

| Finding | What was wrong | Test |
|---|---|---|
| TYPES-4, medium | A subfolder scan (`/codebase-audit:audit src/billing`) never read the manifests or `docs/agents/audit-signals.tsv` above it, so lenses the root scan fires were reported skipped | `test_subfolder_scan_reads_the_repo_manifests_and_house_signals_above_it` |
| FAILURE-2, medium | An empty or hand-written `SCAN.md` made verify's "every fired lens has a findings file" check pass with nothing checked | `test_scan_md_that_names_no_firing_lens_fails` |
| SECURITY-1, medium | Folder and file names from the audited repo went unquoted into the analyzer commands the scan prints | `test_analyzer_commands_quote_the_repo_paths_they_carry` |
| PERFORMANCE-1, medium | Seed patterns with `.*` cost the square of a line's length: 14.4 s for one 300 KB minified file, now 0.15 s | `test_minified_line_is_not_seeded_and_later_lines_keep_their_numbers` |
| TESTS-1, medium | 20 of 32 hand mutations of `scan.py` and `verify.py` survived the suite, among them guards the fundamentals table names; 2 survive now, both with unchanged output | the tests added in `tests: go red on the checks the README names as guards` |
| TYPES-1, low | A signals row with an unknown type matched nothing and `--check` said `ok` | `test_unknown_row_type_is_refused_with_file_and_line` |
| TYPES-2, low | Python `a, _ = f()` counted as a swallowed error | `test_python_tuple_unpacking_is_not_a_swallowed_error` |
| TYPES-3, low | A site after blank lines was reported on the first blank line with an empty snippet | `test_site_points_at_the_matching_line_past_blank_lines` |
| TYPES-5, low | `verify.py --lens "types, money"` skipped ` money` without a word | `test_lens_filter_refuses_a_lens_that_does_not_exist`, `test_lens_filter_allows_spaces_after_commas` |
| SECURITY-2, low | `--since=--output=x` made git write a file into the audited repo | `test_since_that_looks_like_an_option_is_refused_and_writes_nothing` |
| DESIGN-3, low | `cochange.sh` read a quoted non-ASCII path as another folder; the script had no test | `tests/test_cochange.py` |
| DESIGN-4, low | The file cache was keyed by relative path, so a second root in one process read the first root's files | `test_same_relative_path_in_two_roots_reads_each_roots_file` |
| TESTS-2, low | Nothing checked that the parallel-monorepo scaffold still gets the plan its grader requires | `test_parallel_monorepo_gets_the_plan_its_grader_expects` |

## Open

### TESTS-3 The skill's main loop is checked only by an unrecorded manual eval
- where: evals/seeded-bugs/case.yaml:1
- probe: critical-gaps
- scenario: a prompt change lowers recall, or the skill never beat an unaided prompt → nothing in the repo shows it: no results are committed, each case runs once, there is no arm without the skill, and every fixture was written for the skill
- severity: medium
- detectability: silent
- verdict: PLAUSIBLE (the suite was not run in this audit)
- fix family: commit one dated results file from `--runs 3 --ablation with-without`, then a run on a pinned third-party repo with known bug-fix commits

### STATE-1 Which lenses ran has two owners, and verify reads one
- where: skills/audit/scripts/verify.py:146
- probe: truth-owner
- scenario: recon drops a lens the scan fired on a false signal, as step 2 of `SKILL.md` allows → verify fails for the missing findings file; recon adds a lens the scan skipped and its hunter never writes → verify passes
- severity: medium
- detectability: quiet
- verdict: CONFIRMED (two calls to `verify.py` with a `SCAN.md` that fires `ux` and no `findings/ux.md`, and one that skips `data`)
- fix family: one owner for the final lens list that verify reads; needs a format decision for `RUN.md`

### DESIGN-1 Shards of one lens must share an id sequence and nothing says so
- where: skills/audit/SKILL.md:56
- probe: implicit-protocol
- scenario: the scan shards a lens across packages → each hunter numbers from 1 and each one's `verify.py --lens` fails on the other's file
- severity: low
- detectability: loud
- verdict: CONFIRMED (`test_two_shards_reusing_an_id_are_told_to_renumber`; the error now names the files and the remedy, the brief still does not prevent it)
- fix family: the dispatcher gives each shard a number range in its brief

### DESIGN-2 Docs state arguments and commands the code does not have
- where: skills/audit/SKILL.md:5
- probe: docs-drift
- scenario: the parallel-monorepo eval passes `--budget 3` to a skill whose argument list has no `--budget`; the README's CI line uses `$PLUGIN_DIR`, which nothing defines, chains verify with `&&` under a sentence that says "its own step", and `--since origin/main` exits "cannot diff" on a depth-1 checkout; `UNTANGLE.md` calls the command `/audit`
- severity: low
- detectability: quiet
- verdict: CONFIRMED (grep for each string)
- fix family: one home for the argument list, and a CI example that has been run once

### TYPES-6 CONFIRMED accepts any existing file as the reproduction
- where: skills/audit/scripts/verify.py:74
- probe: parse-at-edge
- scenario: `verdict: CONFIRMED (read it, see SCAN.md)` passes, and a finding `LOL-1` in `money.md` passes
- severity: low
- detectability: silent
- verdict: CONFIRMED (both run against `verify.py`)
- fix family: require the reproduction under `<out>/repro/` or a test path, and the id prefix to match the lens; this tightens what existing audits pass, so it is a decision

### FAILURE-1 When git fails the scan walks the folder and still says "tracked"
- where: skills/audit/scripts/scan.py:223
- probe: silent-catch
- scenario: git refuses the repo (dubious ownership in a container) or is absent → the scan lists files by walking the folder, ignored files included, with no notice
- severity: low
- detectability: silent
- verdict: PLAUSIBLE (the no-git half was run; the dubious-ownership case was not)
- fix family: say in the scan header which listing was used

### OPERATIONS-1 The plugin job installs whatever claude-code is latest
- where: .github/workflows/ci.yml:28
- probe: ci-gates
- scenario: a new release turns the icon warning into an error → every pull request goes red for a reason unrelated to its change
- severity: low
- detectability: loud
- verdict: PLAUSIBLE
- fix family: pin the version and bump it on purpose

### OPERATIONS-2 Dependabot proposes bumps to planted eval fixtures
- where: evals/parallel-monorepo/fixtures/repo/packages/api/package.json:1
- probe: dependency-updates
- scenario: pull request 15 bumps express in a fixture that is never installed; a merged bump changes an eval's ground truth, while the workflow's own actions have no update schedule
- severity: low
- detectability: quiet
- verdict: PLAUSIBLE
- fix family: a Dependabot config that covers the actions and leaves `evals/**/fixtures` alone

Refuted: PERFORMANCE-2 (the file cache holds every source file): bounded by the repo's own source under 1 MB per file, and gone with the process.

Not covered: the eval suite was not run; history was not scanned for secrets; whether the CI checks are required on `main` could not be read.

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
