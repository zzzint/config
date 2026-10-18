---
name: large-scale-execution
description: "Piloting, phase discipline and evidence when fanning work out to many subagents — read before orchestrating"
---

# Running work across many agents

This one has no trigger. Nothing fires it; it only helps if it gets fetched before
a large fan-out, which means it is the least reliable rule here. Read it when a
plan is about to be split across more than a handful of workers.

Start from a plan that names every item, which phases depend on which, what runs
in parallel, what contract the workers share, and what has to be green before
moving on. Do not fan out while a real product or architecture question is still
open — the workers will each answer it differently.

Before repeating the same shape of work many times, run two or three real units all
the way through: an ordinary one, an awkward one, and the riskiest variation. Send
them through the whole path — the same brief, the same isolation, the same
integration, the same checks. Keep what they produce; it is real output, not a
rehearsal. If a pilot turns up an ambiguity, fix the brief and run it again before
going wide.

Run everything within a phase at once when the units are genuinely independent. Do
not serialize work that has no dependency, and do not invent parallelism where
there is a dependency.

A worker saying it finished is not evidence. Read the diff, the logs, the
artifacts. Check the combined result after the slices come together, not just each
slice on its own — repeat a worker's own check only when its evidence is missing,
stale, or does not cover integration.

When output comes back wrong or thin, send corrective work rather than quietly
fixing it yourself and losing the signal that the brief was bad.

Inside a plan that has already been approved, do not stop at phase boundaries to
ask whether to keep going. Stop only for a genuine decision, a change in what is
authorized, or an external thing that tools cannot resolve.
