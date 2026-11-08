---
name: parallel-monorepo
description: Runs the audit on a two-package TypeScript monorepo seeded by scaffold.sh (needs --scaffold) with 200 filler modules, so the scan plans parallel subagents within a budget of 3 and shards the types lens across both packages. Grades that the plan is parallel, hunters run as subagents, verify.py passes, and the three planted defects are found.
tags: [core, offline, parallel]
plugins: ["../.."]
runs: 1
expected_outcome: The scan's plan is parallel; the failure and types hunts run as subagents; the report finds the swallowed save error with a false "Saved" toast, the `default:` that lets refunded orders ship, and the read-then-write stock race.
model: sonnet
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Write, Edit, Bash, Agent, Skill]
---

/codebase-audit:audit --lens failure,types --budget 3

When you're done, tell me the scan's plan line, how the hunts ran, the last line `verify.py` printed, and every finding with its file, severity and verdict.
