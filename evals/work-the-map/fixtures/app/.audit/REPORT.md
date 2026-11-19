# Audit report

## Fundamentals
- F1 not checked: the run was `--lens money,state`
- F2 not checked: the run was `--lens money,state`
- F3 not checked: the run was `--lens money,state`
- F4 broken: MONEY-1, STATE-1, MONEY-2
- F5 not checked: the run was `--lens money,state`
- F6 not checked: the run was `--lens money,state`
- F7 not checked: the run was `--lens money,state`
- F8 not checked: the run was `--lens money,state`
- F9 not checked: the run was `--lens money,state`
- F10 not checked: the run was `--lens money,state`
- F11 not checked: the run was `--lens money,state`
- F12 not checked: the run was `--lens money,state`
- F13 not checked: the run was `--lens money,state`
- F14 not checked: the run was `--lens money,state`

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
