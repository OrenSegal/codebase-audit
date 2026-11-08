---
name: work-the-map
description: Resumes an audit from an existing .audit/HANDOFF.md (seeded by scaffold.sh, needs --scaffold) whose next step is the audit map in .scratch/. Grades that the run resumes instead of re-auditing, works exactly one frontier ticket test-first until its repro is green, records the resolution on the ticket, the map and the hand-off, and leaves the user's decision ticket alone.
tags: [core, offline, handoff]
plugins: ["../.."]
runs: 1
expected_outcome: Ticket 01 is claimed and resolved with an Answer; src/webhook.js verifies the HMAC signature and deduplicates by event id; the repro and the suite pass; the map's Decisions so far gains a line; HANDOFF.md names ticket 02 next; ticket 03 (grilling) stays open; no new full audit is run.
model: sonnet
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Write, Edit, Bash, Agent, Skill]
---

/codebase-audit:audit

When you stop, print the output of `node --test 'test/*.test.js' '.audit/repro/*.test.js'`, the header lines of each ticket file, the map's Decisions so far, and the `next:` line of `.audit/HANDOFF.md`.
