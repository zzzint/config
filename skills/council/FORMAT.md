# Page

The page (`REPORT.html`) is the review. It brings the facts of each case and a recommended change; it takes no position on what the reader does next. Plain sentences, ordinary words. The reader is technical but has not opened the diff; each card must carry enough to judge the finding without leaving it.

Every `file:line` is a link to `https://github.com/<owner>/<repo>/blob/<head-sha>/<path>#L<n>`; a spec disagreement links the doc line beside it.

The page runs top to bottom in this order, and nothing else appears on it:

1. **High level context** (the header on the page) — what the PR accomplishes, in two to four plain sentences a reader who has not seen the diff can follow: the problem it addresses, what it changes, and what a user or operator gets that they did not have before. No judgement in this paragraph.
2. **Direction** — headed by the question *Is this the right direction?* and answered *Yes.* · *Maybe.* · *No.* — separate from whether the code is right. Green bar for Yes, amber for Maybe, red for No, so the answer reads before the words do. *Maybe* is for a direction that is defensible but not yet shown to be right — a decision still open, an alternative not yet weighed — and the reasoning must say what would settle it. Then two or three sentences of why, from the premise seat's findings after the skeptic. When a premise finding survived, this names it and links to its card. The counts line follows: how many cards in each group, and how many nits. Nothing about the process appears on the page — no seat or skeptic counts, no verdict words; what the skeptic found goes into the Finding it settled. The one exception is the seat tag on each card and nit, which names the lens that found it.
3. **Primer** — what the cards assume the reader knows, taught before the cards need it (`TUTOR.md`).
4. **Cards**, grouped by action — *Do before merge*, then *Decide*, then *Verify in #N*. Each card carries its group as a coloured bar on its left edge, the same treatment as the Direction box: red, amber, purple. No badge text; the group heading above the run of cards names it.
5. **Nits** — findings that are true and the author may or may not act on: a naming, a duplicated helper, a fixture that misleads, a doc sentence that overclaims. One sentence each, seat-tagged, with a cite. The test for landing here is consequence: a finding with any consequence a user or operator would see — a silent outage, a wrong classification, a cancelled turn that keeps working — is a card, however small its fix, and its group says what to do with it. Nothing is demoted into this section to save space.

There is no praise section and no stack-notes section. A decision that is genuinely right and load-bearing is stated in Essence or Direction where it belongs; process record — what the skeptics killed, what closed a ledger entry — goes in the ledger, not on the page.

# Card

A card, in the order the template holds it:

- **#N · title** — what goes wrong, in plain words; the card's left bar carries its group. Then the seat tag(s): which lens found it. This is the one place a seat name appears on the page, kept because it tells the reader what kind of problem this is at a glance.
- **Context** — one sentence: what this code is for and what it is trying to guarantee. Priming, not the finding.
- **Where** — `file:line` (and the spec line if it disagrees).
- **Finding** — two or three sentences. Mechanism first, then consequence in user/operator terms. "Nothing today, but…" when that is the truth.
- **Recommendation** — the change, concretely: the shape of the fix, the smallest version that closes it. When the right answer is a decision rather than a change, say what the decision is and what each side implies.
- **Fix size** — one line, and honest: "one statement plus one test", "two sentences in the changeset", "a separate PR". Name the durable fix separately when it is bigger than the smallest one.
- **Judgement call** — present only when one decision would make the finding evaporate: "if `/playground` is the console's chat surface for this release, this drops to a doc fix." One sentence naming the decision and what it does to the finding.

**Groups.** Every card is in exactly one: **Do before merge** is the review's position that this must land first. **Decide** is everything else that survived: the reviewer and author make the call, and the card gives them what they need — the finding, the fix size, the judgement call. **Verify in #N** is a finding that depends on a later PR in the stack. There is no group for findings the review has already decided against; a finding that survived the skeptic earned a look. For a stacked PR, cards still open from an earlier page are carried forward into their group, tagged with the PR number they came from and linking to that page, so the findings read across the stack.

**A type finding is a finding.** It is graded and placed like any other — a card, or a nit if it has no consequence, tagged `types` — never a section of its own. When a type change is the fix for another seat's finding, it goes into that card's Recommendation (the one-statement fix first, then the durable shape), not beside it.

**Severity is internal.** Seats file findings as `block` · `fix` · `question` (behavior may be intended; the doc doesn't say) · `verify` (depends on a later PR in the stack) · `nit` (true, no consequence anyone would see), and skeptics uphold, demote, or escalate within that same list. The chair maps each survivor to a group: `block` → *Do before merge*; `fix` → *Do before merge* unless its judgement call or fix size says a fast-follow is honest, then *Decide*; `question` → *Decide*; `verify` → *Verify in #N*; `nit` → the Nits section. The page shows the group, never the severity; how bad it is, the Finding paragraph says.

There is no cap on cards. A finding is a card because a skeptic upheld it with a consequence, and the skeptic is what keeps the count honest; a page with fifteen cards is telling the reader something true about the PR. Cards group by action, never by seat; an empty group is omitted.

# Language

One test governs every sentence on the page: **a reader who has not opened the diff and was not in the review, reading this sentence alone, knows what it says.** [`EXAMPLE.html`](EXAMPLE.html) is a full page that passes it; match it.

- **Full sentences.** Subject, verb, full stop. A list of fragments is not a sentence: "upheld — shipped, supported, in the promise" fails; "Upheld. The web component is a shipped, supported surface, and the spec's 'every embed' claim includes it." passes.
- **No review-coined shorthand.** If a seat or skeptic started calling something "the promise", "the seam", "the authority", the page says the thing itself: the spec sentence, the repository method, the service that decides.
- **Name things as the code and docs name them.** A file, a function, a route, a doc line — never a role the review assigned.
- **One idea per sentence.** A semicolon or dash joining two findings is two sentences.
- **Reader-facing consequences.** "The client is told its acceptance succeeded when it was not recorded" over "an audit-integrity defect." Jargon only when it is the codebase's own term.

Three checks, in order, before the page opens:

1. **Mechanical floor** — `python3 floor.py <page>` from this folder; exit 0 or fix. Outside `<dd class="where">`, every `<dd>` ends in a full stop and is at least five words; every nit's text before its trailing cite ends in a full stop.
2. **The editor** (one sub-agent, template in [`EDITOR.md`](EDITOR.md)): receives the rendered page and this section, and nothing else — no diff, no seat reports, no review context. It is the stranger the test names. It returns each failing field rewritten, or marked *cannot be rewritten from the page alone*, which means the chair left out a fact.
3. **The chair applies the editor's rewrites** and supplies the missing facts for the fields it could not rewrite. A field is never trimmed to pass; it is rewritten.

# Comment voice (on request only)

The page never drafts comments. When the user asks for one on a specific card, draft it in chat, in their voice — at most two sentences: the mechanism as the reader would meet it, then the question. A remedy appears only when the user has said they want the change.

- **Question-shaped.** State the mechanism plainly, then ask whether it is wanted. The shape that landed: *"Does this effectively mean that if a tool call fails, and that same tool is later called with completely different args, we're marking the original failure as recovered? Is that the behavior we want?"*
- **Advocacy when a change is wanted:** *"I'd advocate we represent case outcomes as a discriminated union of some kind — something like `kind: "scored" | "pipeline_error" | "runner_exception"`. It would give consumers the ability to tell 'the agent got it wrong' from 'the infrastructure failed' without digging through failure strings."* Name the design move ("represent … as"), not the edit ("make this").
- **Name the mechanism precisely.** "the judge", not "the model used by the eval engine" — a vague noun invites a "no, that part is deterministic" misread of a good question.
- **One hedge, not three.** "I'd wonder if that's problematic — models tend to…" not "I'd wonder if that could be problematic in that a model may have some…".
- **Anchor.** Every draft names the file:line it goes on. Doc drift comments name both the doc line and the code line.
- **No "in this PR" / no pointing at consumers** unless the user asks; the why is the rigor it adds, in one clause.
- **Nits lead with `nit:`** so a new colleague reads calibration, not a gate.

Have the reply in your pocket: for each draft, one sentence on what the author will likely say back and whether it changes anything (e.g. "this only applies to `retryable: true` failures — your question still stands because the match is name-only").
