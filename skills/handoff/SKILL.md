---
name: handoff
description: Write a handoff note so a fresh session or another agent can pick up a piece of work cold, in plain, followable language. Use when the user says "hand this off", "write a handoff", "leave notes for next time", or is about to end, compact, or move a session; and when passing a workstream to another worktree or agent.
---

The state of one workstream is written down for a reader who has no memory of this session: a future session, another agent, or the user next week. The output is a note that lets that reader continue without rediscovering anything. It adds no new work and starts nothing.

A handoff differs from a `brief` in who reads it. A brief is for someone who was here and stepped away; it leans on shared context and ends with a question. A handoff assumes none of that context. It spells out the things a brief can take for granted, and it carries the traps and the working commands that a newcomer would otherwise hit and rediscover.

## Resolve the scope first

With no argument, the scope is the current session's goal. With an argument, find exactly which workstream it names. Ask where the note should go only if the user has not said and the repo has no convention for it; otherwise print it in chat, so the user decides where it lives. Never write it into a project's specs, ADRs, or docs unless asked — in a repo where those are the plan, a handoff file there becomes a second plan.

## Gather before writing

Look, do not remember: the todo list, running jobs, uncommitted changes with `git status`, the branch and its latest commits, and the last result of each check. The reader will act on this note without the ability to ask what you meant, so every claim must be one they can confirm.

## Structure

Use these headings, in this order. Omit a heading only when it is genuinely empty, and then say so in one word ("None.").

**Goal.** What the work is for, in one or two sentences, quoting the user's words where they exist. Name the governing document — the spec section, the issue, the ADR — and tell the reader to read it rather than paraphrasing it.

**Where it stands.** Branch, worktree path, last commit, and whether the tree is clean. Then what is finished, with the evidence for each item, and what is half-done, with exactly where it stopped.

**Next steps.** Ordered. Each one concrete enough to start on: the file, the function, the command. Mark which are safe to do alone and which need the user's authorization.

**Traps.** What cost time this session and will cost it again: a check that passes without running the changed code, a stale build that has to be restarted, a misleading count, a doc that is out of date. Each with what happened and how to avoid it.

**Commands that work.** The exact commands for build, test, typecheck, and run that were used and observed to work this session, with the working directory. Not the ones the docs suggest — the ones that ran.

**Open questions.** Decisions still waiting on the user, each in one line with what it blocks. A handoff does not ask them; it records them.

**Do not touch.** Files or areas owned by another session or agent, and actions that need authorization the next reader does not yet have.

## Language

Plain, coherent, followable, and complete on its own. Write each sentence so it still makes sense to someone who did not see the conversation: no "the issue above", no "as discussed", no names the session coined. Name things as the code, docs, and tools name them, in backticks. Give paths in full. Mark each claim's footing: observed now, observed earlier this session, or reported and unchecked.

Prefer a slightly long note that the reader never has to question over a short one that sends them back to the transcript.

## Example

Invocation: `/handoff`

**Goal.** Add per-key rate limiting to the public API. Governing record: issue #412, "Rate limit API keys". Read it before starting; do not work from this summary.

**Where it stands.** Branch `api-rate-limit`, worktree `~/code/shop-api`, last commit `a1b2c3d` "Add token bucket limiter". Tree has one uncommitted file, `src/middleware/rateLimit.ts`, with the response headers half-written.
- Done: the token bucket allows a burst of 20 and refills at 5 per second; `npm test -- limiter` passed, 9 tests (observed now).
- Half-done: the middleware is written but not registered on the router; stopped before editing `src/app.ts`.

**Next steps.**
1. Finish the `RateLimit-*` response headers in `rateLimit.ts`. Safe alone.
2. Register the middleware in `src/app.ts`, after authentication so the key is known. Safe alone.
3. Run `npm run typecheck && npm test`. Safe alone.
4. Turn it on in staging. Needs the user's authorization.

**Traps.**
- `npm test` uses an in-memory store, so a limiter that passes there can still fail against Redis. Run `npm run test:integration` with `docker compose up redis` before calling it done.
- The dev server does not reload middleware changes. Restart it before checking a response by hand.

**Commands that work.** From `~/code/shop-api`: `npm run typecheck`; `npm test -- limiter`; `docker compose up redis`, then `npm run test:integration`.

**Open questions.** Whether internal service keys are exempt from the limit. Blocks the exemption check in step 2.

**Do not touch.** `src/auth/` — another session is changing how keys are loaded.

*(Illustrative: names, commit, and results stand in for what a real handoff would read off the repo.)*
