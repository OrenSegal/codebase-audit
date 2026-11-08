---
type: llm
weight: 1
---

`src/items/realtime.ts` waits 250ms after subscribing. The comment gives a live external reason (an upstream realtime bug) and a removal condition (upgrade past 2.47). It is a justified workaround.

PASS if the final response does not mention this delay, or mentions it as a justified workaround to keep (possibly with a note to track the upgrade or name the upstream issue).

FAIL if the response recommends removing the delay as a defect without acknowledging the documented reason, or ranks it among the most severe findings.
