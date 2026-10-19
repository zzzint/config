# Page

The page (`REPORT.html`) is the review: the facts of each case, a recommended change, and two drafted comments per card. The reader is technical but has not opened the diff, so each card stands on its own.

Every `file:line` links to `https://github.com/<owner>/<repo>/blob/<head-sha>/<path>#L<n>`. A spec disagreement links the doc line beside it.

Top to bottom, and nothing else:

1. **Header.** `h1`: repo, PR number, title. `p.meta`: stack position, head short SHA, review date. Then:
   - **High level context** (`p.essence`) — ≤4 sentences: the problem, what the PR changes, what a user or operator gets. No judgement.
   - **Is this the right direction?** (`p.verdict.yes|maybe|no`) — **Yes.**, **Maybe.** or **No.**, then ≤3 sentences of why. Separate from whether the code is right. *Maybe* says what would settle it. A surviving `design` finding is named and linked to its card.
   - **Counts** (`p.counts`) — cards per group, then nits.
2. **Primer** — collapsed, ≤3 concepts the cards assume ([`TUTOR.md`](TUTOR.md)).
3. **Cards** by group: *Do before merge*, *Decide*, *Verify in #N*. An empty group is omitted.
4. **Nits** — true, with no consequence a user or operator would see. Any such consequence (a silent outage, a wrong classification, a cancelled job that keeps working) makes it a card, however small the fix.
5. **Tray** — sticky: picked count and **Copy selected**, which copies each picked draft as markdown under a link to the diff line it lands on. Picks and edits persist per PR head. The page reads fine with JS off.
6. **Footer** — the template's fixed line.

No praise, no stack notes. A right, load-bearing decision belongs in the context or direction. Process never appears: no seat or skeptic counts, no verdict words. What a skeptic found goes into the Finding it settled. Lens tags are the one exception. Process record goes in the ledger.

# Card

`<article class="card do|decide|verify" id="f<N>" data-cite="<path>:<line>">`, in template order:

- **#N · title** (`h3`) — what goes wrong, in plain words.
- **Why** (`p.why`) — exactly 1 sentence: the consequence a user or operator sees.
- **Tags** (`div.tags`) — a `span.tag` per lens that found it (`design`, `shape`, `correctness`, `types`, `safety`, or an elective's short name). Then an `a.assumes` link, "assumes: <concept>", to each primer concept the card relies on. A card carried from an earlier PR adds a "from #M" tag linking to that page, the only link to another page.
- **Pick** (`fieldset.pick`) — radios *Ask*, *Direct*, *Skip*, then **Lands on** (`p.lands` > `a.lands`), then the two drafts (§ Comments). Default: *Ask* for do and decide, *Skip* for verify.
- **Where the comment lands** (`data-cite` and `a.lands`) — the line the comment is posted on, linked into the PR's *Files changed* view: `https://github.com/<owner>/<repo>/pull/<N>/files#diff-<sha256 hex of the path>R<line>` (a range is `R<a>-R<b>`). It must be a head-side line inside a hunk of `PR<N>.diff`, because GitHub attaches inline comments only there. Prefer the added line that causes the problem. When the problem lives outside the diff (a doc the PR did not touch), anchor on the diff line that made it stale. When no diff line fits, use `data-cite="PR"`, linking to the PR with the text "the PR conversation". The landing line can differ from the Evidence `Where` cites, which point at the source for reading.
- **Evidence** (`details.evidence`, collapsed) — a `dl` with exactly these labels:

| Label | Cap | Holds |
|---|---|---|
| Context | 1 sentence | What this code is for and guarantees. Priming, not the finding. |
| Where | links | `file:line`, plus the spec line if it disagrees. |
| Finding | ≤4 sentences | Mechanism, then consequence. "Nothing today, but…" when true. |
| Recommendation | ≤3 sentences | Smallest fix, then the durable fix if bigger. For a decision: name it and what each side implies. |
| Fix size | terse | "One statement plus one test." "A separate PR." |
| Judgement call | optional, ≤2 | The one decision that would make the finding evaporate. |
| Reply | ≤2 sentences | What the author will likely say back, and whether it changes anything. |

A **nit** (`li#n<N>[data-cite]` in `ul.nits`): unchecked checkbox, lens `span.tag`, `span.text` (1 sentence), `span.where` holding its `a.lands` link (same rule as a card), and a `div.draft` starting `nit:` (≤2 sentences, § Comments).

**Groups.** Every card is in exactly one. **Do before merge**: the review's position that this lands first. **Decide**: everything else that survived. Reviewer and author make the call. **Verify in #N**: depends on a later PR in the stack. In a stack, cards still open from an earlier page carry forward into their group.

**Severity is internal.** Seats file `block` · `fix` · `question` (may be intended, the doc doesn't say) · `verify` (depends on a later PR) · `nit` (no visible consequence). Skeptics move findings within that list. The chair maps survivors:

- `block` → *Do before merge*
- `fix` → *Do before merge*, or *Decide* when its judgement call or fix size makes a fast-follow honest
- `question` → *Decide*
- `verify` → *Verify in #N*
- `nit` → Nits

The page shows the group, never the severity.

**A type finding is a finding**, placed like any other and tagged `types`. When a type change fixes another lens's finding, it goes into that card's Recommendation: the one-statement fix, then the durable shape.

**No cap on cards.** A card exists because a skeptic upheld its consequence. Cards group by action, never by lens.

# Comments

Every card carries both framings in the user's voice. The user picks one, edits it, copies it. Each draft is ≤2 sentences, plain markdown (code in `` `backticks` ``), and pastes as written.

**The voice**, taken from comments the user actually posted. It is curious and collaborative, and it plants an idea at a high level rather than issuing a verdict.

- **Lead with the question or a tentative read, never a flat verdict.** Not "X calls Y, so Z throws. Should we…?" Instead, ask about the mechanism directly, or say what it *looks like*, then ask.
- **Soften the observation, not the question.** "This looks to be…", "This feels like…", "It looks like…", "Presuming…", "I'm assuming… If that's right, …"
- **Leave the author room.** "Is that handled somewhere, or should…?", "Is there anything stopping us from…?", "Is there intentionality behind…?", "Would it make sense to…?", "What do you think about…?", "I'm hesitant to… unless…".
- **Say "we".** "How do we reconcile this with…", "Wondering if there's some way we may…", "I'd advocate we…".
- **High level first, few code names.** At most three code spans in a draft and no code snippets. Name the thing the author will recognise, then the consequence in plain words.
- **Point at the source naturally** when it helps: "Reading `ADR 0017`, it looks like…", "From 0016 (line 15)…".
- **One hedge, not three.** "I'd wonder if that's problematic — retries tend to…" not "I'd wonder if that could be problematic in that a retry may have some…".
- **Name the mechanism precisely.** "the scheduler", not "the part that decides when work runs again". A vague noun invites a "no, that part doesn't retry" misread.

Posted comments that are the model, with identifiers swapped for neutral ones:

> Is there intentionality behind how `account_id` is structured in each of these tables? Specifically around enforcing `NOT NULL` but not enforcing a foreign key.

> Can this `.8` default ever be reached, given the `validateInput` early-return at the top of this function?

> Does this effectively mean that if a job fails, and that same job is later run with completely different arguments, we're marking the original failure as recovered? Is that behavior we want?

> Now that we have `error` logs show up in Sentry as issues, would this log + throw combo result in two separate issues?

> This and the newly added `parseRetryDelay` look to be identical. Perhaps worth consolidating in to some shared utility?

> I'd advocate we represent job outcomes as a discriminated union of some kind — something like `kind: "succeeded" | "failed" | "crashed"`. It would give consumers the ability to tell "the job got it wrong" from "the infrastructure failed" without digging through failure strings.

Three kinds of draft, all in the voice above:

- **Ask** (`data-framing="ask"`) — question-led, in the shapes above. Contains `?`. A remedy appears only as a question ("Should we release the lock there?").
- **Direct** (`data-framing="direct"`) — still gentle, but takes a position. Open with the softened read ("It looks like…", "This looks to be at odds with…"), then the position: "I'd advocate we…", "I'd wonder if we want…", "Perhaps worth…?", "We have an opportunity here to…". Name the design move ("represent … as"), not the edit ("make this"). Never a bare imperative or a flat verdict.
- **Nit** (the nit's `div.draft`) — starts `nit:`, so a new colleague reads calibration, not a gate. Then one light sentence in the same voice: "nit: looks like `X` isn't used anywhere. Perhaps worth dropping?", "nit: some references we may want to update here: …", "nit: is this commenting out intentional?". A small question or a "may want to" beats a flat statement of fact.

All three:

- **Anchor.** The draft is written for its landing line (`a.lands`), and Copy puts a link to that line above it. A doc-drift draft also names the doc line.
- **No "in this PR", no pointing at consumers.** The why is the rigor it adds, in one clause.
- **Vary the shapes across a page.** The voice is a range, not a template. Rotate openers ("Is there…", "Can this…", "Does this effectively mean…", "Presuming…", "It looks like…", "This feels like…", "Would it make sense…", "Wondering if…"), and let some drafts be a single plain question. No opening phrase starts more than a quarter of a page's drafts. Read the drafts top to bottom before finishing: if they sound stamped from one mould, rewrite the repeats.

**Reply** (in Evidence, never in a draft) is the answer in the user's pocket: "This only applies to retried jobs. The question still stands because the match is by name only."

# Language

One test: **a reader who has not opened the diff and was not in the review, reading this sentence alone, knows what it says.** [`EXAMPLE.html`](EXAMPLE.html), a fictional `acme/shop-api` review, passes (`python3 floor.py EXAMPLE.html --diff EXAMPLE.diff`); match it.

Checked fields: `p.essence`, `p.verdict`, `p.why`, every Evidence `dd` except `dd.where`, both drafts, nit `span.text` and drafts, primer `p.idea` and `p.here`.

- **Short sentences.** Prose ≤25 words a sentence, drafts ≤35. A `<code>` or backtick span is one word. A link counts by its text.
- **Sentence counts** as capped above.
- **One idea per sentence.** No `;` and no spaced dash (` — `) in a checked prose field. Drafts are exempt: they are in the user's own voice, which uses dashes.
- **Full sentences.** Subject, verb, full stop. Every checked field ends with `.` (a draft may end `?`) and has ≥5 words, except Fix size. "upheld — shipped, supported, in the promise" fails. "The web component is a shipped, supported surface. The spec's 'every embed' claim includes it." passes.
- **No review-coined shorthand.** Not "the promise" or "the seam". Say the spec sentence, the method, the service.
- **Name things as the code and docs name them.** Never a role the review assigned.
- **Reader-facing consequences.** "The client is told its acceptance succeeded when it was not recorded" over "an audit-integrity defect."
- **No links to other pages**, except a carried-forward card's "from #M" tag.

A run-on Finding, split:

> BEFORE: The read and the write are two separate commands with nothing tying them together, so two instances that read at the same moment both see one token left and both admit their request, which lets a burst go past the limit by one request per instance.
>
> AFTER: The read and the write are two separate commands. Two instances that read at the same moment both see one token left. Both admit their request, so a burst can go past the limit.

Three checks before the page opens:

1. **Floor** — `python3 floor.py <page> --diff /tmp/<repo>-<N>/PR<N>.diff` from this folder enforces the caps and checks every landing line is in the diff. Exit 0 or fix.
2. **Editor** — one cold sub-agent ([`EDITOR.md`](EDITOR.md)) with the page and § Language and § Comments only. It returns failing fields rewritten, or MISSING when the page lacks a fact.
3. **Chair** — applies rewrites, supplies every MISSING fact, runs the floor again. Never trim a field to pass. Rewrite it.
