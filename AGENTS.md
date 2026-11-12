# Working on codebase-audit

Before committing a change to a skill, lens, pattern or script, all of these pass:

```bash
python3 skills/audit/scripts/scan.py --check
python3 -m unittest discover tests
claude plugin validate .
```

After changing `SKILL.md`, a lens, the router, the finding format, `DELIVER.md` or `UNTANGLE.md`, also run the eval suite (about 5 minutes and $3 at `-j 3`):

```bash
claude plugin eval . --scaffold --runs 1 --ablation none -j 3 --allow-tools Bash Write Edit Agent
```

| Case | Covers |
|---|---|
| `seeded-bugs` | full sequential audit: recall on 8 planted defects, severity, a fence it must keep |
| `parallel-monorepo` | parallel plan with a sharded lens, hunters as subagents, `verify.py` passing |
| `untangle-orders` | `--untangle` end to end: single source for copied values, green tests, one commit per fix |
| `work-the-map` | resume from `HANDOFF.md`, one approved ticket fixed test-first, map and hand-off updated |
| `resume-unapproved` | resume with no approval: asks first, changes no source |

What the suite does not show: no results are committed (`evals/results/` is git-ignored), each case runs once, the fixtures are a few small files written for this skill, and `--ablation none` runs no arm without the skill, so a pass says the skill completed the case, not that it beat an unaided prompt. Add `--runs` and an ablation arm before quoting a number.

`tests/test_evals.py` checks, without calling a model, that every scaffold builds its workspace from a clean clone.

To run a subset, filter by tag (`--tag untangle handoff`); `--case` takes one glob and its last occurrence wins.

Each fact has one home; the table in `README.md` says where. Edit it there and point to it from everywhere else.
