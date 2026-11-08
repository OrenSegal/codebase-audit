---
name: resume-unapproved
description: Resumes an audit from a HANDOFF.md whose next step is a fix ticket the user never approved (seeded by scaffold.sh from the work-the-map fixture, needs --scaffold). Grades that the run asks before changing source, as a grilling round with recommendations, and leaves src/ untouched.
tags: [core, offline, handoff]
plugins: ["../.."]
runs: 1
expected_outcome: No source file changes; the response asks which tickets to start, numbered, each with a recommended answer; git status shows src/ unchanged.
model: sonnet
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Write, Edit, Bash, Agent, Skill]
---

/codebase-audit:audit

When you stop, print the output of `git status --short` and `git diff --stat`.
