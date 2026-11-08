# Working on codebase-audit

Before committing a change to a skill, lens, pattern or script, all of these pass:

```bash
python3 skills/audit/scripts/scan.py --check
python3 -m unittest discover tests
claude plugin validate .
```

After changing a skill, a lens, the router, the finding format or `DELIVER.md`, also run the eval suite (about 5 minutes and $3 at `-j 3`):

```bash
claude plugin eval . --scaffold --runs 1 --ablation none -j 3 --allow-tools Bash Write Edit Agent
```

| Case | Covers |
|---|---|
| `seeded-bugs` | full sequential audit: recall on 8 planted defects, severity, a fence it must keep |
| `parallel-monorepo` | parallel plan with a sharded lens, hunters as subagents, `verify.py` passing |
| `untangle-orders` | `untangle` end to end: single source for copied values, green tests, one commit per fix |
| `work-the-map` | resume from `HANDOFF.md`, one approved ticket fixed test-first, map and hand-off updated |
| `resume-unapproved` | resume with no approval: asks first, changes no source |

To run a subset, filter by tag (`--tag untangle handoff`); `--case` takes one glob and its last occurrence wins.

Each fact has one home; the table in `README.md` says where. Edit it there and point to it from everywhere else.
