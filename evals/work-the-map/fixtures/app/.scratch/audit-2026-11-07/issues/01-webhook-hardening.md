Type: fix
Status: open
Blocked by:

## Fix
Verify the webhook signature (HMAC-SHA256 of the raw body with the shared secret, hex) and deduplicate events by id, so only genuine, first deliveries grant credits. A bad signature returns 400.

## Findings
- MONEY-1 `src/webhook.js:3`: grants credits with no signature check.
- STATE-1 `src/webhook.js:5`: a redelivered event grants credits again.

## Done when
`.audit/repro/webhook.test.js` goes from red to green, and the full suite stays green.
