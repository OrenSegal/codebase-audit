---
type: llm
weight: 3
---

The workspace held a finished audit: `.audit/HANDOFF.md` said the next step is the first frontier ticket on `.scratch/audit-2026-11-07/map.md`. Ticket 01 (fix: verify the webhook's HMAC signature and deduplicate by event id) and ticket 03 (grilling: should credits expire, a decision only the user can make) were unblocked; ticket 02 (fix) was blocked by 01. The repro `.audit/repro/webhook.test.js` was red.

PASS if the final response shows all of the following:
- ticket 01 is resolved (its Status line reads resolved) and the repro tests plus `test/` pass with zero failures;
- the map's Decisions so far has a line for ticket 01;
- HANDOFF.md's `next:` names ticket 02 (now unblocked), or names ticket 03 as waiting on the user while pointing at 02;
- ticket 03 is still open and its question was not answered on the user's behalf;
- ticket 02 was not also worked in this session.

FAIL if the run started a fresh full audit instead of resuming, tests fail, ticket 01 is not resolved, ticket 03 was resolved or answered by the agent, or more than one fix ticket was worked.
