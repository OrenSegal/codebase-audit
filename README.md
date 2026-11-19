# codebase-audit

An adversarial codebase audit for Claude Code and any host that reads Agent Skills. It fingerprints the project, holds it to fourteen engineering fundamentals through 122 probes in 14 lenses, has each serious finding challenged by a separate refuter, scores every fundamental in the report, delivers the fixes as a ticketed map, and untangles the structure. It reads and reports first; it changes source only for tickets you approve.

## At a glance

| | |
|---|---|
| **Install** | Two commands, under [Install](#install); Python 3.9+ and git, nothing else |
| **Run** | `/codebase-audit:audit` for the whole repo; `--since origin/main` for a PR; `--untangle` for the structural refactor; run it again to resume |
| **Checks** | The [fourteen fundamentals](#fundamentals-the-audit-checks) below, each through named probes; eight lenses always run, six more fire when the scan finds their stack |
| **Proves** | Each serious finding is either reproduced (`CONFIRMED`, with a red test or script) or survives a refuter on reasoning (`PLAUSIBLE`); killed ones are listed in `refuted.md` |
| **Checks itself** | `verify.py` fails an audit with an unanswered probe, a finding pointing at a missing file, an unreproduced `CONFIRMED`, a finding missing from the report, or a scorecard that skips a fundamental or calls a broken one fine |
| **Writes** | Only `.audit/` (git-ignored) and the issue tracker (`.scratch/` by default) until a ticket is on the `approved:` line |
| **Does not** | Prove a finding true (`verify.py` checks shape and completeness), install analyzers, write to production systems, or replace a human security review. Its recall and precision on real codebases [have not been measured](#evidence) |

## Install

Claude Code:

```bash
claude plugin marketplace add OrenSegal/codebase-audit
```

```bash
claude plugin install codebase-audit@codebase-audit
```

The scripts need Python 3.9 or newer and git; they use only the standard library.

Other hosts (Codex reads `agents/openai.yaml`; Cursor, Windsurf): copy `skills/audit/` into the host's skills directory. The fix routes name mattpocock-skills; without them, the audit does each step inline.

## Fundamentals the audit checks

The rules the audit holds your codebase to. Every probe in every lens tests exactly one of them (`scan.py --check` fails otherwise), so no probe is unowned and no rule goes unchecked. `REPORT.md` opens with a scorecard: each rule `holds`, `broken` with the finding ids, or `not checked` with the reason. The table's home is `skills/audit/SKILL.md`; `test_readme_fundamentals_match_skill` keeps this copy identical.

| # | Fundamental | Checked by (`lens.probe`) |
|---|---|---|
| F1 | **Correct on every input.** The empty, the one, the maximum, the negative, the missing and the non-ASCII input all give the right answer | `correctness.boundaries`, `correctness.null-paths`, `correctness.numeric`, `correctness.equality-identity`, `correctness.inverted-logic`, `correctness.text-encoding`, `correctness.regex`, `correctness.copy-paste`, `correctness.ignored-result`, `ux.cardinality`, `ux.locale-adversary`, `ai.wrong-meaning`, `ai.adversarial-input` |
| F2 | **Parse at the edge; make illegal states unrepresentable.** Outside data becomes a domain type once, at the boundary, and the types forbid what the domain forbids | `types.parse-at-edge`, `types.primitive-obsession`, `types.stringly-typed`, `types.boolean-blindness`, `types.optional-soup`, `types.catch-all`, `types.units-and-time`, `types.assumption-ledger`, `money.money-arithmetic` |
| F3 | **One source of truth per fact,** enforced where the fact is stored; every copy derives from it or is reconciled with it | `design.copies`, `state.truth-owner`, `types.schema-twin`, `data.constraints`, `money.entitlement-source`, `money.truth-table` |
| F4 | **State changes are explicit, idempotent and order-safe.** Every write is harmless the second time and correct when it arrives late, at midnight or across a time zone | `state.state-machine`, `state.runs-twice`, `state.out-of-order`, `state.calendar-adversary`, `money.counter-integrity`, `money.store-webhooks` |
| F5 | **Concurrency and partial failure leave consistent data.** No read-then-write race, no data race, no half-finished multi-step write | `failure.await-race`, `failure.shared-memory`, `failure.pull-the-plug` |
| F6 | **Fail loud, recoverably, and never lie to the user.** No swallowed error, no spinner forever, no copy that promises what the code does not do | `failure.silent-catch`, `failure.no-screen`, `failure.timeouts-retries`, `failure.dependency-outage`, `ai.fail-safe-direction`, `ux.copy-lie`, `ux.dead-ends`, `ux.no-undo`, `ux.interrupted-user`, `ux.day-2-day-30`, `money.paywall-honesty`, `ux.a11y-extremes` |
| F7 | **Trust nothing from outside; grant least privilege.** Every entry point authenticates, authorizes and validates; secrets stay secret; dependencies are vetted | `security.secrets`, `security.injection`, `security.crypto`, `security.local-storage`, `security.transport`, `security.entry-points`, `security.sessions`, `security.confused-deputy`, `security.abuse`, `security.web-surface`, `security.mass-assignment`, `security.audit-trail`, `security.supply-chain`, `data.user-b`, `ai.output-as-instructions`, `operations.secrets-handling` |
| F8 | **Personal data is minimal, declared, protected and deletable** | `security.privacy-flows`, `data.delete-account`, `data.sensitive-at-rest`, `ai.data-sent-out` |
| F9 | **Every resource is bounded.** Time, memory, storage, connections, concurrency and spend grow with the input, never without limit | `performance.main-thread`, `performance.startup`, `performance.render`, `performance.quadratic`, `performance.query`, `performance.network`, `performance.memory`, `performance.backpressure`, `correctness.resource-leak`, `state.lifetime`, `data.unbounded-growth`, `ai.cost-bounds`, `operations.cost-runaway` |
| F10 | **Every change is compatible and reversible.** Old clients and old data keep working, a bad release rolls back, and lost data can be restored | `evolution.old-client`, `evolution.local-migrations`, `evolution.rollback`, `evolution.kill-switch`, `evolution.forced-update`, `evolution.config-drift`, `evolution.platform-drift`, `data.migration-on-real-data`, `tests.contract`, `design.public-api`, `operations.backup-restore` |
| F11 | **Every check can go red, and runs on every change.** Tests fail on the regressions that matter; CI gates block; builds reproduce | `tests.delete-test`, `tests.mutation`, `tests.classify`, `tests.critical-gaps`, `tests.property-candidates`, `tests.runs-in-ci`, `ai.evals`, `operations.ci-gates`, `operations.reproducible-build`, `operations.dependency-updates` |
| F12 | **Modules are deep, and what changes together lives together.** Small interfaces over real behavior, dependencies point toward stability, nothing is surplus | `design.global-state`, `design.scattered-feature`, `design.implicit-protocol`, `design.internals-coupling`, `design.dependency-direction`, `design.caller-vocabulary`, `design.shallow-module`, `design.pass-through`, `design.speculative-generality`, `design.dead-code`, `design.special-cases` |
| F13 | **Code says what it means, and docs say what the code does.** One name per concept, readable functions, comments only for what code cannot show, docs a newcomer can follow | `design.naming-drift`, `design.readability`, `design.comments`, `design.docs-drift`, `design.onboarding` |
| F14 | **Production is observable and operable.** When it breaks at 3am, something pages, the logs say why, and on-call knows the first step | `failure.logs-only-debug`, `operations.alerting`, `operations.runbooks` |

## Fundamentals this repo holds itself to

The rules this plugin holds its own code to, each with the check that proves it. A rule without a passing check is a finding, not a claim; [AUDIT.md](AUDIT.md) says which ones held on the last audited commit.

| # | Fundamental | Checked by |
|---|---|---|
| 1 | One home per fact. Copies derive from it or a test ties them | `scan.py --check`; `test_readme_lens_table_matches_lens_files`; `test_manifests_share_one_version`; the table under [Single source of truth](#single-source-of-truth) |
| 2 | Done is checked, not claimed. A missing or partial output fails | `verify.py`; `test_missing_output_directory_fails`, `test_no_findings_and_no_scan_fail`, `test_scan_md_that_names_no_firing_lens_fails`, `test_lens_that_fires_in_the_scan_needs_a_findings_file`, `test_garbage_audit_fails` |
| 3 | Runs where it says it runs: Python 3.9 and later, `git`, no installs | CI runs the unit tests on 3.9 and a current Python; `test_no_analyzer_command_downloads_its_rules` |
| 4 | Every check runs on every change | the commands in [AGENTS.md](AGENTS.md); `.github/workflows/ci.yml` runs all but the eval suite |
| 5 | A test goes red on the regression it guards | `python3 -m unittest discover tests`; the eval suite for prompt changes |
| 6 | Parse at the edge and fail loud: bad input exits with `file:line` or a usage error, never a silent default | `scan.py --check`; `test_missing_root_exits_2`, `test_budget_below_one_is_refused`, `test_unknown_row_type_is_refused_with_file_and_line`, `test_bad_regex_is_refused_with_file_and_line`, `test_lens_filter_refuses_a_lens_that_does_not_exist`, `test_blank_severity_is_a_missing_field_not_a_crash` |
| 7 | Scope is what it claims: `--since` covers every changed file, committed or not, and a subfolder scan still reads the manifests and house signals above it | `test_since_includes_staged_and_untracked_files`, `test_since_keeps_changed_paths_with_spaces`, `test_since_on_a_subfolder_finds_its_changed_files`, `test_subfolder_scan_reads_the_repo_manifests_and_house_signals_above_it` |
| 8 | Cost grows with the input, not its square | `test_since_diffs_once_per_scan`, `test_minified_line_is_not_seeded_and_later_lines_keep_their_numbers`; review for the rest |
| 9 | Read-only until approved: output stays in `.audit/`, source changes need the `approved:` line | the `resume-unapproved` eval; `test_resume_unapproved_has_the_hand_off_without_approval` |
| 10 | Docs match the code: every documented command runs, every path exists | `test_readme_lens_table_matches_lens_files`, `test_readme_fundamentals_match_skill`; the design lens's docs-drift probe |
| 11 | Nothing is unowned: every probe tests one fundamental, and every report scores every fundamental | `scan.py --check`; `test_check_reports_unmapped_and_unknown_probes`; `test_scorecard_must_score_every_fundamental`, `test_scorecard_cannot_say_a_broken_fundamental_holds` |

## Usage

| Command | Does |
|---|---|
| `/codebase-audit:audit` | Full audit of the repo: scan, recon, every lens that fires, verify, report, deliver the map |
| `/codebase-audit:audit src/billing --lens money,state` | Only those lenses, only that path |
| `/codebase-audit:audit --since origin/main` | Only what changed: a PR review, or a re-audit after fixes |
| `/codebase-audit:audit --untangle [area or ticket]` | The structural refactor (`UNTANGLE.md`): pieces that change together end up together |
| `/codebase-audit:audit` again | Resumes from `.audit/HANDOFF.md`: works the next approved ticket, or asks |

Every argument, including `--fix` and `--out DIR`, is defined in step 1 of `skills/audit/SKILL.md`. The skill is user-invoked, so it costs no context until you call it.

**In CI** (or any `claude -p` run), unanswered questions stay on `HANDOFF.md`, tickets go to the local tracker only, and no source changes without approval. Gate the job on `verify.py` as its own step. It fails when the audit left no output, a lens that fired has no findings file, a probe is unanswered, a finding points outside the repo or at a missing file, a `CONFIRMED` verdict names no reproduction file that exists, the report omits a finding, or the report's fundamentals scorecard skips a rule or says one holds that a finding breaks. It checks that the output is complete and well-formed, not that a finding is true:

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
| Verify | Merge duplicates; one claim-only refuter per serious finding; promote by reproduction (`CONFIRMED`) or reasoning (`PLAUSIBLE`); a coverage critic sends thinly covered critical paths back for a second look | `refuted.md`, which `verify.py` requires beside the report and checks against the findings |
| Report | A scorecard of the fourteen fundamentals; fixes above the findings they solve, ranked by severity (set by who can trigger it) then detectability; structural fixes in deep-module terms; trend since the last audit; proposed project-local seed rows | `verify.py` on the whole output |
| Deliver | An audit map plus one typed ticket per fix with blocking edges, on the repo's tracker (local `.scratch/` by default) | `HANDOFF.md` names the next ticket |
| Fix | Each ticket routed to `tdd`, `UNTANGLE.md`, `grill-with-docs`, `improve-codebase-architecture`, `codebase-design`, `wayfinder`, `to-tickets` or `diagnosing-bugs`; source changes only for tickets on `HANDOFF.md`'s `approved:` line | the ticket's repro goes green |
| Re-audit | `--since <audit commit>` on the touched lenses | verifies with no critical or high left |

Every phase rewrites `.audit/HANDOFF.md`, so any session, or the next skill, can resume.

## Lenses: when they fire, and which probes are conditional

Each lens file opens with a `Fires:` line; probes marked *(when …)* are conditional and close as `n/a` with a reason when the condition does not hold. Unconditional probes are always answered.

| Lens | Fires | Unconditional probes | Conditional probes |
|---|---|---|---|
| correctness | always | boundaries, null-paths, numeric, equality-identity, inverted-logic, resource-leak, text-encoding, regex, copy-paste, ignored-result | none |
| types | always | parse-at-edge, primitive-obsession, stringly-typed, boolean-blindness, optional-soup, catch-all, units-and-time, assumption-ledger | schema-twin |
| state | always | state-machine, runs-twice, truth-owner, lifetime | out-of-order, calendar-adversary |
| failure | always | silent-catch, no-screen, logs-only-debug, timeouts-retries | await-race, shared-memory, pull-the-plug, dependency-outage |
| security | always | secrets, injection, crypto, transport, supply-chain, privacy-flows | local-storage, entry-points, sessions, confused-deputy, abuse, web-surface, mass-assignment, audit-trail |
| performance | always | main-thread, quadratic, memory | startup, render, query, network, backpressure |
| tests | always | critical-gaps, property-candidates, runs-in-ci | delete-test, mutation, classify, contract |
| design | always | copies, global-state, scattered-feature, implicit-protocol, internals-coupling, dependency-direction, caller-vocabulary, shallow-module, pass-through, speculative-generality, dead-code, special-cases, naming-drift, readability, comments, docs-drift, onboarding | public-api |
| data | a database, server API or storage bucket | unbounded-growth | constraints, user-b, migration-on-real-data, delete-account, sensitive-at-rest |
| evolution | a client that cannot be force-updated, on-device data, or a database | rollback, config-drift, platform-drift | old-client, local-migrations, kill-switch, forced-update |
| ai | model output entering the app | wrong-meaning, adversarial-input, fail-safe-direction, output-as-instructions, cost-bounds, evals | data-sent-out |
| money | purchases, subscriptions, credits or plan limits | truth-table, entitlement-source, money-arithmetic, paywall-honesty | counter-integrity, store-webhooks |
| ux | a user interface | cardinality, day-2-day-30, copy-lie, dead-ends, no-undo, a11y-extremes | interrupted-user, locale-adversary |
| operations | CI, deployment or infrastructure config | ci-gates, secrets-handling, dependency-updates, reproducible-build | backup-restore, alerting, runbooks, cost-runaway |

Routing is pattern matching over file paths, manifests and source (`signals.tsv`), so it is as good as its rows: a stack or SDK with no row gets the eight always-on lenses and no candidate sites until a row is added, and recon can override a lens the scan fired or skipped. The scan has detection rows for iOS, Android, Flutter, React Native, web, Node, Python, Go, Rust and Ruby. Lockfiles, fixture folders and build or vendor folders are not read for routing; the scan's `not read for routing` line lists them. Files over 1 MB are not read, and lines over 1,000 characters (minified bundles, embedded data) are not searched for candidate sites; the scan does not list those.

The lens files are the source of truth for this table; `scan.py --check` fails if a `Fires:` line disagrees with the routing, and `test_readme_lens_table_matches_lens_files` fails if this table drifts from them.

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
| Version | `.claude-plugin/plugin.json` (`test_manifests_share_one_version` ties the other two manifests to it) |
| Fundamentals the audit checks, and the probes under each | `skills/audit/SKILL.md` (copied in [Fundamentals the audit checks](#fundamentals-the-audit-checks); `test_readme_fundamentals_match_skill` ties the copy) |
| Fundamentals this repo holds itself to, and their checks | `README.md`, [Fundamentals this repo holds itself to](#fundamentals-this-repo-holds-itself-to) |
| Whether each fundamental holds, and the open findings | `AUDIT.md` |

## Extending it

- **A probe**: add `- **probe-id**: question` (or `- **probe-id** (when <condition>): question`) to a lens file, add `` `<lens>.<probe-id>` `` to one row of the Fundamentals table in `SKILL.md` and its copy here, and optionally a `seed` row with id `<lens>.<probe-id>`.
- **A lens**: add `lenses/<name>.md` with a `Fires:` line, and a `signal` row that fires it (or add it to `ALWAYS` in `scan.py`).
- **A stack, SDK, or house pattern**: a `stack`, `signal` or `seed` row; project-specific rows go in the audited repo's `docs/agents/audit-signals.tsv` (the report proposes them).
- **An analyzer**: a `tools.tsv` row: tool, lens, the file that makes it relevant, `root` or `package`, command.

Then run the checks in `AGENTS.md`.

## Output

Everything goes to `.audit/` in the audited repo, ignored by its own `.gitignore`: `SCAN.md`, `RECON.md`, `RUN.md`, `HANDOFF.md`, `tools/`, `findings/`, `refuted.md`, `repro/`, `REPORT.md`, `untangle-log.md`, and `history/` with earlier runs. The map and tickets go to the issue tracker (`.scratch/audit-<date>/` when local).

## Evidence

None is published yet. `evals/` holds five cases on small seeded fixtures (see `AGENTS.md`), but no results are committed, each case runs once, and there is no run without the skill to compare against. There is no measurement of recall, precision or false positives on a real codebase. It is a set of instructions to a model plus two checking scripts.

## Credits

- `UNTANGLE.md`, the structural taxonomy and comment rules in `lenses/design.md`, and the test classes in `lenses/tests.md` are adapted from [caldoai/skills `untangle-codebase`](https://github.com/caldoai/skills) (MIT, Copyright (c) 2026 Maze); see `NOTICE`.
- Vocabulary and hand-off shapes from [mattpocock/skills](https://github.com/mattpocock/skills): codebase-design, wayfinder, to-tickets, grilling, handoff.
- Verification follows the claim-only refuter and runtime-validation pattern of [Refute-or-Promote](https://arxiv.org/pdf/2604.19049).
- Lens prompts draw on [awesome-falsehood](https://github.com/kdeldycke/awesome-falsehood), the fallacies of distributed computing, Hyrum's law, STRIDE, and [OWASP MASVS](https://mas.owasp.org/).

## License

MIT. Third-party text is listed in `NOTICE`.
