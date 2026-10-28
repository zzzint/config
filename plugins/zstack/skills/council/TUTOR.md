# Tutor

One read-only sub-agent, spawned after the page is written and before the language checks. It writes the **Primer**: at most three concepts, each taught because **a card on this page assumes it**. The Primer is standalone. It never links to, or assumes, an earlier review or primer, and nothing about it is recorded between runs.

## Input

The finished page, the clone at `/tmp/<repo>-<N>`, `PR<N>.diff`, the head SHA, and the spec / design doc path.

## Instruction (verbatim skeleton)

```
# Role
You are writing the Primer for a code-review page. The reader is a strong engineer who is new to this codebase and has read nothing else about it. Teach the few ideas the cards assume, so the cards make sense on first read.

# Selection
Read every card. List each concept a card relies on that a strong engineer new to this repo would not know: a runtime primitive (a job queue, a serverless worker), a domain idea (a billing period, an order state machine), a house pattern (how tenancy is scoped, how a repository CAS works), or a general idea the reasoning depends on (optimistic concurrency, fail-closed, cooperative cancellation). Keep at most 3: the ones the most cards rely on, most foundational first. If none qualify, return "no primer".

# Each entry
- name: as the code and docs name it.
- idea: exactly 1 sentence, the general idea, true in any codebase.
- here: at most 2 sentences, how this repo does it, with a link to the head-SHA blob line that defines or best shows it.
- read: optional, one link to the doc section or external reference worth opening next.

# Constraints
READ-ONLY. Never invent a mechanism. If you cannot find where a concept lives, drop it and say so in your notes.
Standalone: no links to other review pages, no "as before", no "already covered".
Plain words, stricter than the cards. Sentences of at most 25 words, one idea each, no ";" and no " — ", ending in ".". The idea sentence uses only ordinary English and ordinary engineering vocabulary (JSON, SQL, a status code, a middleware). The here sentences may use this repo's names, each shown as <code> with its cite.

# Output
1. The HTML block below, one <section> per concept.
2. Per concept slug, the card ids that assume it (e.g. "p-token-bucket: f1, f4").
3. Notes: concepts cut by the cap or dropped for lack of a cite, with the cards that use them.
```

Output block, matching the template:

```html
<details id="primer">
<summary>Primer — 2 concepts this page assumes</summary>
<section class="primer" id="p-<slug>">
  <h3><code>AbortController</code></h3>
  <p class="idea"><span class="k">idea</span> One sentence, the general idea.</p>
  <p class="here"><span class="k">here</span> At most two sentences, with a <a href="https://github.com/<owner>/<repo>/blob/<head-sha>/<path>#L<n>"><code>path:n</code></a> link.</p>
  <p class="read"><span class="k">read</span> <a href="…">One link.</a></p>
</section>
</details>
```

`<slug>` is the name in lowercase, words joined by `-`. `p.read` is optional.

## Chair's use of the result

- Insert the block between the direction box and the cards. With "no primer", omit `details#primer`.
- Add `<a class="assumes" href="#p-<slug>">assumes: <name></a>` to each listed card's `div.tags`.
- For a concept in the notes, make sure each card using it says the term plainly in its own words.
- The Primer then goes through the floor and the editor with the rest of the page ([`FORMAT.md`](FORMAT.md) § Language).
