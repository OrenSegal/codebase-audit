---
type: llm
weight: 3
---

The audited app has eight planted defects:
1. `supabase/migrations/001_items.sql`: the select policy `using (true)` lets any signed-in user read every user's items.
2. `src/webhooks/stripe.ts`: no signature verification and no event-id deduplication, with a read-then-write credit increment, so a replayed or forged webhook grants credits.
3. `src/scan/quota.ts`: the pro flag and the scan counter live in localStorage, so they can be reset or forged on the client.
4. `src/items/status.ts`: the `default:` branch shows the "recalled" status as "Fresh".
5. `src/items/sync.ts`: an empty catch swallows the save error, then the toast says "Saved" anyway.
6. `src/items/expiry.ts`: date-string comparison in UTC and 86400-second days give wrong expiry near midnight or across DST.
7. `src/billing/price.ts`: money as floats, rounded per line.
8. `test/price.test.js`: the only test asserts `true` and cannot fail.

PASS if the final response identifies at least six of the eight (by file or by an unmistakable description of the mechanism), and rates defect 1 critical or high.

FAIL if it identifies fewer than six, rates defect 1 medium or low or omits it, or reports findings in files that do not exist.
