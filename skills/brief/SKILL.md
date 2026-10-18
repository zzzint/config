---
name: brief
description: Brief the user on where a piece of work stands, in plain, followable language. Use when the user asks "where are we", "brief me", "catch me up", "what's the state of this", or returns to a session after time away; and before asking for a decision that depends on the overall state rather than on one item.
---

The state of one workstream — usually the current session's goal — is laid out for a smart colleague who stepped away and is coming back. The output is a short, structured snapshot. It adds no new work, starts nothing, and drafts nothing. Where `contextualize` explains one thing, a brief covers the whole of the work and how its parts stand.

## Resolve the scope first

With no argument, the scope is the current session's goal. With an argument — "the migration work", "where's the auth refactor" — find exactly which workstream it names. If it fits two, take the one most recently worked on and say in one line which was chosen. If the session has no clear goal, say so in one line and brief on what was actually done instead.

## Gather before writing

A brief is only as true as what stands behind each line. Before writing, look at the current state rather than remembering it: the todo list, running jobs and agents, the worktree's uncommitted changes, recent commits, and the last result of any check. A line that rests on memory of earlier in the session, rather than on something just looked at, says so.

## Structure

Use these headings, in this order, each one to five short lines. Omit a heading only when it is genuinely empty, and then say so in one word ("None.").

**Goal.** What the work set out to do, quoting the user's words where they exist. If the goal shifted during the session, give the current one and say in one line what it replaced.

**Done.** Each finished item with the thing that shows it: the file and line, the command and what it covered, the commit. An item a subagent reported but nobody has looked at goes under **In flight**, not here.

**In flight.** What is started and unfinished, running in the background, or reported but unchecked. Say which of those each one is.

**Blocked or waiting.** What cannot move, on what or whom, and what would unblock it.

**Changed since you last looked.** What the user has not yet seen: new findings, a plan that moved, something that broke. On a first brief in a session, this is "First brief."

**Next.** Up to three steps, each with one line of why.

**Ask of you.** Either "None." or the one open decision, appended after this heading in the five-part shape the working agreement requires: **Decision**, **Context**, **Options**, **Recommendation**, **Question**. One decision at most.

## Language

Plain, coherent, followable. The overall verdict first — on track, stuck, or drifted — in one sentence before the headings, so the reader knows how to read the rest. Then the detail.

Name things as the code, docs, and tools name them, in backticks. Prefer counts and names that were seen over characterizations ("3 of 5 tests pass", not "mostly working"). Mark each claim's footing: observed now, observed earlier this session, or reported and unchecked. Never promote a report to a fact by restating it.

A brief is a snapshot, not a history. Do not narrate the order things happened in unless the order is what matters.

## Example

Invocation: `/brief`

On track, with one blocker that needs you.

**Goal.** "Move the nightly order export off cron and onto the job queue" — the export should retry on failure instead of silently skipping a night.

**Done.**
- `ExportOrdersJob` runs the export on the queue and retries three times with backoff; `npm test -- export` passed, 14 tests (observed now).
- The cron entry is removed from `deploy/crontab` (observed earlier this session).

**In flight.**
- A subagent reports it updated the runbook in `docs/operations/exports.md`. Not yet read.

**Blocked or waiting.**
- The production queue worker has a 60-second job timeout, and the export took 4 minutes on last week's data. Raising the timeout is a production config change and needs your authorization.

**Changed since you last looked.** The old cron job had been failing two nights in seven for a month; nothing checked its exit code. Those failures will now show up in the job queue's failure list.

**Next.**
- Read the subagent's runbook change — it is the only unchecked claim.
- Run the export once against a copy of last week's data — the tests use a 20-row fixture and say nothing about runtime.

**Ask of you.**
**Decision:** How to fit the export inside the queue worker's job limit.
**Context:** Above, under Blocked.
**Options:** Raise the production job timeout to 10 minutes; or split the export into one job per day of orders.
**Recommendation:** Raise the timeout — it is one config line, and splitting the job changes the output files downstream consumers read.
**Question:** May I raise the production queue timeout to 10 minutes?

*(Illustrative: the names, counts, and results stand in for what a real brief would read off the work.)*
