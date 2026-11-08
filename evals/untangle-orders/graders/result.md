---
type: llm
weight: 3
---

The app started with these planted structural problems:
1. Order statuses copied three times: `src/ui/badge.js` (LABELS), `src/api/serialize.js` (STATUSES) and `src/reports/export.js` (KNOWN, which is missing "refunded", so refunded orders export as "unknown").
2. `src/db/repo.js` is a pass-through over `src/db/store.js`.
3. `src/legacy/csv.js` is dead code.
4. `formatTotal(cents, forReport)` in `src/money/format.js` takes a flag only the report understands.
5. In `test/orders.test.js`, "repo reads through the store" is tied to internals, and "orders module loads" cannot fail.

PASS if the final response shows all of the following:
- the statuses now come from one source that badge, serializer and export all use, and refunded orders export correctly (called out as a behavior change or bug fixed);
- at least three of problems 2, 3, 4 and 5 were fixed, with the cannot-fail test removed;
- `node --test` output with zero failures;
- `git log --oneline` with more than one commit after the initial "orders app" commit.

FAIL if tests fail, there is a single squashed commit, the status lists still exist separately, or the printed `node --test` or `git log` output contradicts the claimed changes.

The special-case counts may legitimately read 0 from `scan.py --special` on this small app; a separate hand count from the decision log is expected, not a contradiction.
