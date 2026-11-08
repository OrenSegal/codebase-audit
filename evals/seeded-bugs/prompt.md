---
name: seeded-bugs
description: Runs the full audit on a small TypeScript and Supabase app seeded by scaffold.sh (needs --scaffold) with eight planted defects across data, money, state, types, failure, UX and tests, plus one documented workaround that must be kept. Grades routing through scan.py, recall on the planted defects, severity of the RLS hole, and respect for the fence.
tags: [core, offline]
plugins: ["../.."]
runs: 1
expected_outcome: The report finds at least six of the eight planted defects listed in graders/recall.md, ranks the `using (true)` select policy critical or high, and leaves the realtime settle delay in place as a justified workaround.
model: sonnet
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Write, Edit, Bash, Agent, Skill]
---

/codebase-audit:audit

When you're done, give me the summary: every finding with its file, severity and verdict.
