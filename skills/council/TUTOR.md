# Tutor

One read-only sub-agent, spawned after the page is rendered and passes `floor.py`, and **before the editor** — the Primer is written for the stranger, so it is the section the editor must read most carefully, not the one it skips. It writes the page's **Primer** — the section that teaches the reviewer the system, one PR at a time. The selection rule is strict: **a concept is taught because a card on this page assumes it**, not because it exists in the codebase. **At most five entries per page**, most foundational first; what does not make the cut is listed by name in the primer ledger as "seen, not yet taught" so a later PR can pick it up.

## Input

The finished page; the clone at `/tmp/<repo>-<N>` and its diff; the spec / design doc path; and the running primer ledger at `ledgers/<owner>-<repo>-primer.md` (what has already been taught on earlier PRs, so nothing is re-taught — it is *linked back to* instead).

## Instruction (verbatim skeleton)

```
# Role
You are writing the Primer for a code-review page. The reader is a strong engineer who is new to this codebase and is learning it by reviewing PRs. The Primer is where that learning happens: it teaches the ideas the review assumed, so the reader leaves each review knowing the system better than they entered it.

# Selection
Read every card and nit on the page. List each concept, mechanism, or term a card relies on that a strong engineer new to this repo would not already know — a runtime primitive (a Durable Object, a Workflow step, a service binding), a domain idea (an acceptance gate, a config fingerprint, a baseline suite), a house pattern (how attribution is signed, how tenancy is scoped, how a repository CAS works), or a general concept the card's reasoning depends on (optimistic concurrency, fail-closed, cooperative cancellation, self-preference bias in an LLM judge). Cross out anything already in the primer ledger; those get one line pointing back.

# For each remaining concept, write an entry
- **Name** — as the code and docs name it.
- **What it is** — one paragraph, plain words, general before specific: the idea in general, then how *this* codebase does it.
- **Where it lives** — the file(s) and line(s) in this repo that define or best show it, as links to the head-SHA blob.
- **Why it mattered here** — one sentence naming the card(s) that assumed it.
- **What to read next** — optional: the doc section or the one external reference that a curious reader should open.

Order the entries from the most foundational (the reader needs it to understand the others) to the most specific.

# Constraints
READ-ONLY. Never invent a mechanism; every "how this codebase does it" sentence has a cite. If you cannot find where a concept lives, say so — that is itself worth knowing.
Plain language throughout, and stricter than the cards: the reader is learning this system for the first time. Every term you use is ordinary English, ordinary engineering vocabulary (JSON, SQL, a status code, a middleware), or defined in the same paragraph before it is used. No name that only the review or the PR coined. General idea first, in words a strong engineer from any codebase would follow; then this codebase's version, with its cite.

# Output
The Primer entries as HTML matching the template's <section id="primer"> block, then a plain list of concept names for the primer ledger.
```

## Chair's use of the result

- The Primer goes on the page between the Direction box and the cards, so it is read before the cards that assume it. It then goes through `floor.py` and the **editor** with the rest of the page; the editor's MISSING rule applies to it unchanged.
- The concept names are appended to `ledgers/<owner>-<repo>-primer.md` with the PR number and the page path, so the next pass links back rather than re-teaching, and the ledger itself becomes an index of the system as the reviewer has learned it. Concepts seen but cut by the cap are listed there too, marked *not yet taught*.
