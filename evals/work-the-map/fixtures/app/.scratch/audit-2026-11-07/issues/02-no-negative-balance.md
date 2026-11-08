Type: fix
Status: open
Blocked by: 01

## Fix
Make `spend` refuse to take a balance below zero.

## Findings
- MONEY-2 `src/ledger.js:7`: `spend` can drive a balance negative.

## Done when
A test proves `spend` past zero is refused and the balance is unchanged; the full suite stays green.
