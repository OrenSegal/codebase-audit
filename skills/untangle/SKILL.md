---
name: untangle
description: Untangle a whole codebase in one pass, so agents working in it read less per change, break less without noticing, and debug faster.
disable-model-invocation: true
argument-hint: "[area, concern, or audit-map ticket]"
---

<!-- Adapted from caldoai/skills untangle-codebase (MIT, Copyright (c) 2026 Maze). -->

Start a thorough refactor of this codebase and complete it to the end.

Treat this as a goal.

When started from an audit-map ticket or `.audit/HANDOFF.md`, read it first: its fix and findings are the starting list, and its done line is part of yours. Hand-offs, the map and ticket format are in the audit skill's `DELIVER.md` (in `../audit/` from this file).

**Why do this at all?**

- **Better output**: agents write better code in a well-structured codebase.
- **Cheaper & faster changes**: agents spend fewer tokens searching and more on the problem.
- **Fewer silent breaks**: agents break less without noticing.
- **Faster debugging**: agents find root causes faster.

## 1. Ask

Besides untangling the codebase, there are two other things you may do:

| Addition | What it does |
|---|---|
| Comments | Remove comments that only restate the code. |
| Tests | Remove tests that wouldn't catch a real bug, and fix the ones that fail without one. |

List these (with their exact descriptions) for the user and ask which ones to do, with both preselected. If the user has already said, or the session runs without interruptions, take both. Then do only those.

## 2. Baseline

Don't change anything yet.

- Run the build, the linter and the full test suite, and record the results. If tests fail now, list them; they are not yours to fix unless the redesign fixes them.
- Run the audit skill's `scripts/scan.py <path> --special` and `scripts/cochange.sh` (in `../audit/` from this file) and record their output in the decision log. Rerun both at the end; the difference is your progress.
- Script a dependency graph that shows what imports what (for example `madge` for JS/TS, `pydeps` or `import-linter` for Python, `go list -deps`, `cargo modules`, a grep over `import` lines for Swift, Kotlin or Dart). Keep the script; you rerun it as you go.
- For every path the redesign will touch that no test exercises, write a characterization test through its public interface first. This is the net that lets step 5 claim behavior is unchanged.
- Read `GLOSSARY.md`, ADRs and `CLAUDE.md`/`AGENTS.md`: use their names for things, and keep each recorded decision unless you find a reason that would have changed it.
- Speak about structure in the deep-module vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**), the same terms the `codebase-design` skill defines, in the log and in every fix.

## 3. List every problem

Don't change anything yet.

If an audit report exists (`.audit/REPORT.md`), start from its `structural` fixes and findings.

Then go through the codebase with the audit skill's `lenses/design.md` (in `../audit/` from this file): its one question, **should these pieces change together?**, and every probe under it (hidden links, needless links, surplus, special cases, naming and readability). Write down every place the code gets the answer wrong, as in the decision log example. Each special case is a requirement the design never accounted for, so use them to work out what the system needs to be.

## 4. Redesign from first principles

Work out the fixes as if the system had known today's requirements from the start. Look for the one fix behind several problems, which often looks nothing like them. Don't fix special cases one by one.

Ask the same thing of every fix, even one that looks better in the code: pieces that change together end up together, pieces that don't aren't tied, and everything depends on what changes less.

Write each fix above the problems it solves, as in the decision log example.

When a fix has competing interface designs, design it twice (the `codebase-design` skill's design-it-twice pattern) and pick by depth, locality and seam placement. When a fix needs a decision that is the user's (it contradicts an ADR, renames a domain concept, or accepts a risk), resolve it with `grill-with-docs`, which records the ADR and glossary terms, before you build it. Where those skills are unavailable, do the same steps inline.

## 5. Fix everything on the list

Work one fix at a time, highest leverage first. After each fix the build and the full suite are green, and the fix is its own commit, so any regression bisects to one decision. New behavior goes test-first at the module's interface (the `tdd` red-green loop). A wide refactor whose blast radius breaks every caller at once goes expand–contract: add the new form beside the old, migrate callers in green batches, then delete the old form.

Remove the special cases the redesign makes unnecessary, and keep the ones the system still needs. Before removing one, find why it was added (`git log -L`, blame, the PR); a reason that still holds means the system still needs it. Don't go looking for bugs separately. A structural fix may fix some along the way, which is fine; record each one in the log as a behavior change.

If the user chose **Comments**, apply the `comments` probe in `lenses/design.md`.

If the user chose **Tests**, do this last, because tests are your regression safety net. A test should fail on a regression, and only then. Give every test a class and act on it, using the `classify` probe in the audit skill's `lenses/tests.md`. Keep the characterization tests from step 2 unless a behavior test now covers the same path.

## 6. Check, and repeat until done

Have subagents run `lenses/design.md` again over the changed code, each given the decision log so settled items stay settled. When the scope is small enough that the audit's scan plans a sequential run, run that check yourself instead. Do not stop until there is nothing worth fixing left.

You're done when:

- As few special cases are left in the system as possible. How many remain is the best measure of how close you are: count them in the decision log's special-case list, and compare `scan.py --special` (a regex floor that misses many kinds) against the baseline.
- A typical change lands in one place: `cochange.sh` pairs across folders are gone or explained.
- Every import is reasonable, and nothing imports anything more volatile than itself.
- Subagents have no issues left that are worth fixing.
- Intended behavior is the same as when you started, apart from bugs the refactor fixed. The baseline suite and characterization tests pass, and every behavior change is in the log.
- When this ran from an audit ticket: the ticket is resolved with its answer, the map's Decisions so far has its line, `HANDOFF.md` names the next frontier ticket, and a re-audit of the touched lenses with `--since <the starting commit>` passes `verify.py` with no surviving critical or high finding.

## Tips

- **Start from a skeleton**: script away the function bodies, so the whole codebase fits in context.
- **Summarize with subagents**: have them summarize parts of the codebase, so you can reason across all of it at once.
- **Enter where leverage is highest**: start with the hot spots from `git log` and the largest `cochange.sh` clusters.
- **Keep a decision log** at `.audit/untangle-log.md`: compaction is less of a problem that way. When the redesign outgrows one session, chart the remaining decisions with `wayfinder` and work them one at a time.
- **Use Git as evidence**: for how often pieces change, and what changes together.

## Decision log example

The list of problems:

```
- `ui/LogoutDialog.tsx:30` waits 100ms after closing and hopes the message input can take focus by then.
- `ui/Toolbar.tsx:40` and `ui/Menu.tsx:22` call the same actions, each with its own check for when they're disabled.
- `checkout/submit.ts:9` depends directly on `payments/stripe.ts`.
- `shortcuts/keymap.ts:18` has a switch with one case per action, separate from the menu's list.
- `ui/CommandPalette.tsx:55` keeps its own list of actions, and it's missing the newer ones.
- `ui/SettingsDialog.tsx:61` sets a global `skipRefocus` flag to stop the logout dialog it opens from sending focus to the message input.
- `history/undo.ts:30` has a special case for every action that can be undone.
- `refunds/refund.ts:22` wraps every Stripe call in `if (order.provider === "paypal")`.
- Every action handler has to call `track()` by hand, and some don't.
- `ui/Toolbar.test.tsx` and `ui/Menu.test.tsx` test the same actions separately.
```

Then with the fixes:

```
- Make the general `Dialog` give focus back to whatever had it before it opened, so the wait and the flag can both go.
  - `ui/LogoutDialog.tsx:30` waits 100ms after closing and hopes the message input can take focus by then.
  - `ui/SettingsDialog.tsx:61` sets a global `skipRefocus` flag to stop the logout dialog it opens from sending focus to the message input.
- Define a `PaymentProvider` interface that Stripe and PayPal both implement, so checkout and refunds no longer know which one they're using.
  - `checkout/submit.ts:9` depends directly on `payments/stripe.ts`.
  - `refunds/refund.ts:22` wraps every Stripe call in `if (order.provider === "paypal")`.
- Make every user action a command with a name, a handler and an undo, so the toolbar, menu, shortcuts, palette and undo history all run from one list.
  - `ui/Toolbar.tsx:40` and `ui/Menu.tsx:22` call the same actions, each with its own check for when they're disabled.
  - `shortcuts/keymap.ts:18` has a switch with one case per action, separate from the menu's list.
  - `ui/CommandPalette.tsx:55` keeps its own list of actions, and it's missing the newer ones.
  - `history/undo.ts:30` has a special case for every action that can be undone.
  - Every action handler has to call `track()` by hand, and some don't.
  - `ui/Toolbar.test.tsx` and `ui/Menu.test.tsx` test the same actions separately.
```
