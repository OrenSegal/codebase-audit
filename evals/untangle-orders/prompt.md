---
name: untangle-orders
description: Runs the audit's --untangle mode on a small CommonJS orders app seeded by scaffold.sh (needs --scaffold) whose tests pass and which hides a status list copied three times (one copy missing "refunded"), a pass-through repo, dead code, a flag parameter only one caller understands, a test tied to internals and a test that cannot fail. Grades the structural outcome, green tests, one commit per fix, and use of the audit skill's scripts and design lens.
tags: [core, offline, untangle]
plugins: ["../.."]
runs: 1
expected_outcome: One source of truth for order statuses that the badge, serializer and export all use (so refunded orders export correctly, logged as a behavior change); the pass-through repo deleted or deepened; legacy/csv.js deleted; the forReport flag replaced; the cannot-fail test removed and the internals test rewritten or removed; node --test green; several commits.
model: sonnet
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Write, Edit, Bash, Agent, Skill]
---

/codebase-audit:audit --untangle

Do both additions. When you're done, print the output of `node --test`, `git log --oneline`, and the special-case counts from before and after.
