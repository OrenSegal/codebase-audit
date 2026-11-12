# codebase-audit

An adversarial codebase audit that adapts to the project, verifies its own findings, delivers fixes as a ticketed map, and untangles the structure. One Agent Skill; any stack (iOS, Android, Flutter, React Native, web, Node, Python, Go, Rust); any host that reads Agent Skills.

## Usage

| Command | Does |
|---|---|
| `/codebase-audit:audit` | Full audit of the repo: scan, recon, every lens that fires, verify, report, deliver the map |
| `/codebase-audit:audit src/billing --lens money,state` | Only those lenses, only that path |
| `/codebase-audit:audit --since origin/main` | Only what changed: a PR review, or a re-audit after fixes |
| `/codebase-audit:audit --untangle [area or ticket]` | The structural refactor (`UNTANGLE.md`): pieces that change together end up together |
| `/codebase-audit:audit` again | Resumes from `.audit/HANDOFF.md`: works the next approved ticket, or asks |

The skill is user-invoked, so it costs no context until you call it.

**In CI** (or any `claude -p` run), unanswered questions stay on `HANDOFF.md`, tickets go to the local tracker only, and no source changes without approval. Gate the job on `verify.py` as its own step:

```bash
claude -p "/codebase-audit:audit --since origin/main" --allowedTools "Read,Grep,Glob,Write,Edit,Agent,Bash(python3 *),Bash(git *)" && python3 "$PLUGIN_DIR/skills/audit/scripts/verify.py" .audit
```

## The pipeline

| Phase | What happens | Checked by |
|---|---|---|
| Scan | `scan.py` detects stacks, packages and signals, decides which lenses fire and why, plans sequential, parallel or waved subagents within a budget, lists the project's own analyzers to run, and lists candidate sites per probe, hottest files first | `scan.py --check`, `tests/` |
| Tools | Installed analyzers (type checkers, linters, secret and vulnerability scanners, dead-code finders) run once; their warnings become leads | output in `.audit/tools/` |
| Recon | Boundaries, who owns each fact, critical paths, house rules (glossary, ADRs), and which conditional probes hold | every heading answered |
| Hunt | One pass per lens, in sequence or as read-only subagents; methods: pre-mortem, inversion, assumption ledger, Chesterton's fence | `verify.py --lens <lens>` per hunter |
| Verify | Merge duplicates; one claim-only refuter per serious finding; promote by reproduction (`CONFIRMED`) or reasoning (`PLAUSIBLE`); a coverage critic sends thinly covered critical paths back for a second look | `refuted.md` |
| Report | Fixes above the findings they solve, ranked by severity (set by who can trigger it) then detectability; structural fixes in deep-module terms; trend since the last audit; proposed project-local seed rows | `verify.py` on the whole output |
| Deliver | An audit map plus one typed ticket per fix with blocking edges, on the repo's tracker (local `.scratch/` by default) | `HANDOFF.md` names the next ticket |
| Fix | Each ticket routed to `tdd`, `UNTANGLE.md`, `grill-with-docs`, `improve-codebase-architecture`, `codebase-design`, `wayfinder`, `to-tickets` or `diagnosing-bugs`; source changes only for tickets on `HANDOFF.md`'s `approved:` line | the ticket's repro goes green |
| Re-audit | `--since <audit commit>` on the touched lenses | verifies with no critical or high left |

Every phase rewrites `.audit/HANDOFF.md`, so any session, or the next skill, can resume.

## Lenses: when they fire, and which probes are conditional

Each lens file opens with a `Fires:` line; probes marked *(when …)* are conditional and close as `n/a` with a reason when the condition does not hold. Unconditional probes are always answered.

| Lens | Fires | Unconditional probes | Conditional probes |
|---|---|---|---|
| types | always | parse-at-edge, primitive-obsession, stringly-typed, boolean-blindness, optional-soup, catch-all, units-and-time, assumption-ledger | schema-twin |
| state | always | state-machine, runs-twice, truth-owner, lifetime | out-of-order, calendar-adversary |
| failure | always | silent-catch, no-screen, logs-only-debug, timeouts-retries | await-race, pull-the-plug, dependency-outage |
| security | always | secrets, injection, crypto, transport, supply-chain, privacy-flows | local-storage, entry-points, sessions, confused-deputy, abuse |
| performance | always | main-thread, quadratic, memory | startup, render, query, network |
| tests | always | critical-gaps, property-candidates | delete-test, mutation, classify, contract |
| design | always | copies, global-state, scattered-feature, implicit-protocol, internals-coupling, dependency-direction, caller-vocabulary, shallow-module, pass-through, speculative-generality, dead-code, special-cases, naming-drift, readability, comments, docs-drift | none |
| data | a database, server API or storage bucket | unbounded-growth | constraints, user-b, migration-on-real-data, delete-account |
| evolution | a client that cannot be force-updated, on-device data, or a database | rollback, config-drift, platform-drift | old-client, local-migrations, kill-switch, forced-update |
| ai | model output entering the app | wrong-meaning, adversarial-input, fail-safe-direction, output-as-instructions, cost-bounds, evals | data-sent-out |
| money | purchases, subscriptions, credits or plan limits | truth-table, entitlement-source, money-arithmetic, paywall-honesty | counter-integrity, store-webhooks |
| ux | a user interface | cardinality, day-2-day-30, copy-lie, dead-ends, no-undo, a11y-extremes | interrupted-user, locale-adversary |
| operations | CI, deployment or infrastructure config | ci-gates, secrets-handling, dependency-updates | backup-restore, alerting, runbooks, cost-runaway |

The lens files are the source of truth for this table; `scan.py --check` fails if a `Fires:` line disagrees with the routing.

## Single source of truth

| Fact | Lives only in |
|---|---|
| Probes, their conditions, each lens's artifact and done line | `skills/audit/lenses/<lens>.md` |
| Detection, routing and seed patterns | `skills/audit/scripts/signals.tsv` (+ a project's `docs/agents/audit-signals.tsv`) |
| Analyzers the audit runs | `skills/audit/scripts/tools.tsv` |
| Finding format, methods, verification, routing table | `skills/audit/SKILL.md` |
| Hand-offs, map and ticket formats | `skills/audit/DELIVER.md` |
| The structural refactor procedure | `skills/audit/UNTANGLE.md` |
| Structural problem taxonomy and comment rules | `skills/audit/lenses/design.md` (`UNTANGLE.md` points to it) |
| Test classification | `skills/audit/lenses/tests.md` (`UNTANGLE.md` points to it) |
| Deep-module vocabulary | `mattpocock-skills:codebase-design` (used, not redefined) |

## Extending it

- **A probe**: add `- **probe-id**: question` (or `- **probe-id** (when <condition>): question`) to a lens file; optionally a `seed` row with id `<lens>.<probe-id>`.
- **A lens**: add `lenses/<name>.md` with a `Fires:` line, and a `signal` row that fires it (or add it to `ALWAYS` in `scan.py`).
- **A stack, SDK, or house pattern**: a `stack`, `signal` or `seed` row; project-specific rows go in the audited repo's `docs/agents/audit-signals.tsv` (the report proposes them).
- **An analyzer**: a `tools.tsv` row: tool, lens, the file that makes it relevant, `root` or `package`, command.

Then run the checks in `AGENTS.md`.

## Output

Everything goes to `.audit/` in the audited repo, ignored by its own `.gitignore`: `SCAN.md`, `RECON.md`, `RUN.md`, `HANDOFF.md`, `tools/`, `findings/`, `refuted.md`, `repro/`, `REPORT.md`, `untangle-log.md`, and `history/` with earlier runs. The map and tickets go to the issue tracker (`.scratch/audit-<date>/` when local).

## Install

Claude Code:

```bash
claude plugin marketplace add OrenSegal/codebase-audit
```

```bash
claude plugin install codebase-audit@codebase-audit
```

Other hosts (Codex reads `agents/openai.yaml`; Cursor, Windsurf): copy `skills/audit/` into the host's skills directory. The fix routes name mattpocock-skills; without them, the audit does each step inline.

## Credits

- `UNTANGLE.md`, the structural taxonomy and comment rules in `lenses/design.md`, and the test classes in `lenses/tests.md` are adapted from [caldoai/skills `untangle-codebase`](https://github.com/caldoai/skills) (MIT, Copyright (c) 2026 Maze); see `NOTICE`.
- Vocabulary and hand-off shapes from [mattpocock/skills](https://github.com/mattpocock/skills): codebase-design, wayfinder, to-tickets, grilling, handoff.
- Verification follows the claim-only refuter and runtime-validation pattern of [Refute-or-Promote](https://arxiv.org/pdf/2604.19049).
- Lens prompts draw on [awesome-falsehood](https://github.com/kdeldycke/awesome-falsehood), the fallacies of distributed computing, Hyrum's law, STRIDE, and [OWASP MASVS](https://mas.owasp.org/).

## License

MIT. Third-party text is listed in `NOTICE`.
