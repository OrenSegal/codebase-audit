# Audit report

## Summary
3 findings: 1 critical, 1 high, 1 medium. Fix first: webhook hardening.

## Fixes
- Verify the webhook signature and deduplicate events by id, so only genuine, first deliveries grant credits. [local, critical]
  - MONEY-1 `src/webhook.js:3` grants credits with no signature check, so anyone can mint credits with one POST.
  - STATE-1 `src/webhook.js:5` a redelivered event grants credits again.
- Make `spend` refuse to take a balance below zero. [local, high]
  - MONEY-2 `src/ledger.js:7` `spend` can drive a balance negative.

## Unclustered findings
None.

## Coverage
See findings/.
