---
name: recap
description: Summarize what the user worked on over a period — a day, "last week", "this week so far", or a date range — from omp session history, git commits and pull requests. Output is one line per stream of work, a bold subject plus a line of context. Use when the user asks for a recap, a summary of their sessions, or what they did over a period. Logging the hours to Jira is the timesheet skill.
disable-model-invocation: true
argument-hint: the period to cover, e.g. "last week", "this week so far", "Oct 13 to Oct 17"
---

Turn a period of session history into a short, honest picture of the work: one line per stream, each saying what the work is and where it stands. The reader is the user, who was there; the recap reminds and orders, it does not explain.

## 1. Fix the window

Read the argument as two local dates. Weeks run Monday to Sunday; "this week" ends today and is still in progress. No argument means last week. State the window as two dates before gathering anything.

The session history and `gh` stamp time in **UTC**; the user works in local time (`date +%Z%z`). Convert those timestamps before giving them a day: an evening merge in Chicago is the next day in UTC, and a recap that files it there is wrong. `git log --date=short` already prints the author's own offset, so its dates need no shift.

## 2. Gather

Run these together. Widen to every project (`project="*"`); the work is rarely in one repo.

- **Sessions.** `await archive.sessions(project="*", limit=500, silent=True)`, kept when the session's life overlaps the window (`created` ≤ end and `modified` ≥ start). Titles name the streams.
- **Prompts.** `await archive.prompts(project="*", limit=500, silent=True)`, kept by `at`. Prompts are the evidence of what happened inside the window; a long session spans weeks, and its title or newest recap may describe work from after it. If all 500 rows fall inside the window, the oldest days are cut off: say so.
- **Recaps.** `await archive.recaps(project="*", limit=500, silent=True)`, kept by `at`. A session's newest recap is where it stood last, not where it stood at the end of the window; for a window in the past, use the last recap written inside it.
- **Commits.** In each repo the sessions ran in: `git log --all --author="$(git config user.email)" --since=<start> --until=<end + 1 day> --pretty='%ad %s' --date=short | sort -u`. Subjects show what was actually built.
- **Pull requests.** In each GitHub repo: `gh pr list --author @me --state all --search "updated:>=<start>" --limit 100 --json number,title,state,createdAt,mergedAt`. Merged, open and closed is the status of most streams.

For a PR the user reviewed rather than wrote, check its author with `gh pr view <n> --json author` before naming whose work it was.

## 3. Group into streams

A stream is one outcome, not one session: a feature stack, a release, a decision, a doc. Several sessions often feed one stream, and one long session can feed several. Group by what the prompts and commits show, attach PR numbers, and give each stream a status:

- merged or released (name the version),
- open (PR numbers),
- local only (branch, unpushed),
- waiting on a decision (name the decision).

Order streams by weight: shipped product work and large open stacks first, then writing and decisions, reviews, explorations, and the user's own tooling last. Fold sessions that produced nothing — a lookup, a one-line answer — into a nearby stream or drop them.

Check every number before it goes in: a version, a PR, a count. Read it from a commit subject or PR field, not from a recap's prose. Where a stream rests on inference — a session mapped by its title alone — mark it in the caveats.

## 4. Write

One bullet per stream:

```markdown
- **Subject in two to four words:** one line of context — what it is and where it stands, with PR numbers or the version.
```

Keep it to one line each; a stream that needs two lines is two streams or too much detail. After the list, one line naming the sources (sessions and prompt counts, the `git log` and `gh pr list` ranges), and at most three caveats: partial coverage, inferred mappings, days with no activity. Days with no session activity are meetings, time off or work done by hand; say they are quiet rather than guessing.

A table by day goes in only when the user asks how the time was spread. Hours belong to the timesheet skill, whose audit counts agent-active time; they are a floor, not time worked.
