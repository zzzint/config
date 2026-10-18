---
name: commit-discipline
description: "What belongs in a commit — fires when a git commit is being composed"
scope: "tool:bash"
condition: "\\bgit\\b[^&|;]*\\bcommit\\b"
interruptMode: "tool-only"
---

# What goes in this commit

One commit is one coherent change. If the message needs "and" to describe it
honestly, it is two commits.

Never carry along unrelated edits, a failed attempt, or half of a phase just
because the files happen to be dirty. Anything not part of this change either
lands in its own commit or waits.

Only commit work that is green. If a check is failing, say so in the message or do
not commit yet.

Say what changed and why it changed. Where a fix exists because something went
wrong in a way the next reader would not guess, put that in the message — a commit
message is the last place a hard-won reason can survive.

A commit authorizes nothing further. It is not permission to push, to open or merge
a pull request, to deploy, or to spend anything.
