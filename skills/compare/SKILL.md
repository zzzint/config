---
name: compare
description: Compare two to four options side by side in plain, followable language, so the user can think a choice through rather than just pick. Use when the user asks "X or Y?", "what are the tradeoffs", "compare these", "which approach", or pushes back on a recommendation and wants to see the alternatives laid out.
---

Two to four options for one choice are set out side by side for a smart colleague who has to own the decision. The output is a short, structured comparison that ends in a recommendation. It adds no new work, implements nothing, and drafts nothing.

A comparison is the **Options** part of the working agreement's five-part decision, opened up for when the user wants to reason about it. It does not replace that shape: if the user needs to choose now, close with it.

## Resolve the choice first

The argument names the options or the choice: "Postgres vs Redis for this", "the two fixes for the timeout", "should we split this module". Pin down the one question the options answer. If the options answer different questions, say so in one line and compare only the ones that compete. If the user named one option, find the real alternatives — including doing nothing, when doing nothing is genuinely viable — and say which ones were added. Cap at four; more than that means the choice has not been narrowed yet, and the comparison says how to narrow it.

## Ground before writing

Each claim about an option rests on something: the code it would touch, a doc, a measurement, a precedent in this repo. Read those before writing. An option's cost is guessed when it has not been looked at, and a guess says "likely". Where the project has already decided — an ADR, a spec, a rule in `AGENTS.md` — an option that contradicts it is shown with that conflict stated plainly, not quietly dropped.

## Structure

**The choice.** One sentence: what has to be decided, and why now.

**The options.** For each, a short paragraph naming it as the code or docs would and saying what it actually is — what changes, in the reader's terms.

**Side by side.** A table only if it genuinely helps the reader compare; otherwise short paragraphs. Rows are the criteria that actually separate the options in this case — never a generic list. Typical ones: what it costs now, what it costs later, what it closes off, what it risks, how hard it is to reverse, what it conflicts with. Leave out any criterion on which every option comes out the same.

**What would change the answer.** The one or two facts that, if they turned out differently, would flip the recommendation. This is what the user should push on.

**Recommendation.** One option and why, in two or three sentences, tied to the criteria above. Say how confident, and on what footing.

**Ask of you.** Either "None." — when the user asked only to understand — or the decision in the working agreement's five-part shape: **Decision**, **Context**, **Options**, **Recommendation**, **Question**, each of the first four one line, since the sections above carry them.

## Language

Plain, coherent, followable. Treat each option fairly: describe it as its best advocate would, then say what is wrong with it. A comparison written to justify a choice already made is a sales pitch. Prefer concrete differences — lines changed, files touched, a failure mode seen — over adjectives like "cleaner" or "more robust". Name things as the code and docs name them, in backticks. Say "likely" where the truth is inferred.

## Example

Invocation: `/compare where to keep user sessions`

**The choice.** Where the web app stores signed-in sessions, now that it runs on three servers instead of one and in-memory sessions sign users out at random.

**The options.**
- **A `sessions` table** in the existing Postgres database.
- **Redis**, added as a new service.
- **Signed cookies**, which keep the session in the browser and store nothing on the server.

**Side by side.**

| | `sessions` table | Redis | Signed cookie |
|---|---|---|---|
| New infrastructure | None | A new service to run and monitor | None |
| Sign a user out everywhere | Delete their rows | Delete their keys | Not possible until the cookie expires |
| Extra work per request | One indexed query | One in-memory lookup | None |
| Size limit on session data | None in practice | None in practice | About 4 KB |

**What would change the answer.** If traffic grows until one extra query per request shows up in database load, Redis earns its running cost. Today the database runs at 15% load.

**Recommendation.** The `sessions` table. It fixes the random sign-outs with no new service, and it keeps the ability to sign a user out everywhere, which password reset relies on. Confidence: high on today's load, which was measured; medium on how fast traffic will grow.

**Ask of you.** None.

*(Illustrative: the load figure and requirements stand in for what a real comparison would measure.)*
