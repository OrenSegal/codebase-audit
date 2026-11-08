---
type: llm
weight: 3
---

The repo is a two-package monorepo (packages/app, packages/api) with 200 generated filler modules and four planted defects (the first three are required):
1. `packages/app/src/sync.ts`: an empty catch swallows the save error, then the toast says "Saved".
2. `packages/api/src/status.ts`: `default: return true` lets a "refunded" (or any new) status ship.
3. `packages/api/src/stock.ts`: read-then-write across `await` lets two concurrent reservations oversell stock.
4. `packages/app/src/theme.ts`: `default:` renders the high-contrast theme as light (optional; credit if found).

PASS if the final response does all of the following:
- reports a parallel plan (subagents), not a sequential one, with the types lens sharded across the two packages;
- says the hunts ran in subagents;
- reports that verify.py passed (a "verified:" line);
- identifies all three required planted defects by file or by an unmistakable description.

FAIL if the plan was sequential, the hunts all ran in the main context, verification failed or was not run, or any of the three required defects is missing.
