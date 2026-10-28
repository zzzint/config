---
name: council
description: Council review of a PR, a PR stack, or the user's review queue — five read-only lens seats, batched skeptics, and a cold-reading editor. Output is a local HTML page of graded cards, each with a questioning and a direct comment draft the user picks from.
disable-model-invocation: true
---

Review a PR the way a **council** would. **Seats** each look through one lens, **skeptics** try to knock down what they found, the **chair** (you) grades what survives, and an **editor** reads the finished page cold. The output is one HTML page per PR. Each card carries two comment drafts, one that asks and one that says it directly; the user picks, edits and copies on the page. This skill never writes to the PR.

**Hard rules:** every sub-agent is read-only (no edits, no git write commands, no installs, no test runs). The chair writes only the `/tmp` clone and the state folder `~/.local/state/council/`, which holds `reports/` and `ledgers/`; create it when missing. Nothing is written beside this file: an upgrade of the plugin replaces this folder. A question answerable by reading more code is answered here, never handed to the user. Do not load other skills.

## Stack ledger

`~/.local/state/council/ledgers/<owner>-<repo>.md` holds one block per stack (a single PR is a stack of one). It opens with one line naming the stack order and passes done, then three sections of one-line entries, each with a `file:line` where one exists:

- `## Open entries (for #N)` — what a later PR must answer: items the body defers ("rides with #M"), consequences traced only so far, follow-ups, separate ticket candidates.
- `## Posted upstream` — comments the user posted that later code could confirm, answer or strengthen.
- `## Closed in #N` — entries this pass answered, with verdict and line, plus what the skeptics and chair killed and why.

## Modes

- **Single** — `<owner>/<repo>#N`.
- **Stack** — a list of PRs, reviewed base → head, one pass per PR, serially, carrying the ledger.
- **Queue** — no PR given. Run `gh search prs --review-requested=@me --state=open --json number,title,repository,author,url,updatedAt`, then per PR `gh pr view <N> --repo <owner>/<repo> --json headRefOid,baseRefName,headRefName,additions,deletions,files` (search has no head SHA). Print a triage table: PR, size, risk paths, stack membership (base branch is another open PR's head), tier. Skip as up to date a PR whose report's `<meta name="council">` `head` equals `headRefOid`. Stacks run serially; independent PRs may run concurrently within the host's agent cap.

Any run that reviews more than one PR (a stack, a list, or the queue) ends with the index: run `python3 index.py` here and open `~/.local/state/council/reports/index.html`, one row per page with direction, scope and counts.

## Steps (per PR)

### 1. Pin

Read `gh pr view <N> --repo <owner>/<repo> --json body,labels,comments,reviews` and the inline threads (`gh api repos/<owner>/<repo>/pulls/<N>/comments`). Note the stack (what "rides with" a later PR is that PR's ledger item), the spec (doc↔code disagreement is a finding), answered threads (never re-raised), open ledger entries, and the PR's `review:` label (glance, advisory or cosigner) for the page's meta.

Check out to `/tmp/<repo>-<N>`. If a local full clone is known (e.g. the cwd's `origin` matches), `git clone <local-path> /tmp/<repo>-<N>`: fast, full history, the user's repo untouched. Otherwise `git clone --shallow-since=<~12 months ago> https://github.com/<owner>/<repo>.git /tmp/<repo>-<N>`. Then `git -C /tmp/<repo>-<N> fetch https://github.com/<owner>/<repo>.git pull/<N>/head` (same `--shallow-since` in the fallback) and check out `FETCH_HEAD`. Not `--filter=blob:none`: blame would cost a network round-trip per blob.

Save `gh pr diff <N> --repo <owner>/<repo>` as `/tmp/<repo>-<N>/PR<N>.diff`. Record the head SHA; every `file:line` on the page links to it.

Done when: the clone is at the PR head with history, `PR<N>.diff` and the head SHA exist, and stack, spec and ledger entries are in hand.

### 2. Triage

**Light**: the five standing lenses. **Full**: those plus electives ([`SEATS.md`](SEATS.md) § Electives), when the diff is large (~400+ changed lines), touches auth, tenancy, migrations, deploy config or public contracts, or has open ledger entries.

Done when: the tier and any electives are chosen.

### 3. Seats

Spawn every seat in **one concurrent batch** from SEATS.md, each with the whole PR, its lens and ledger entries, and the shared context verbatim. Meanwhile read the one change that would flip the direction if it is wrong.

Done when: every seat has reported.

### 4. Pre-filter and dedupe

Drop findings anchored `pre-existing` into the ledger; a serious one becomes a separate ticket candidate. Merge same-line findings across lenses into one, carrying every lens tag. A pointer ("see correctness: file:line") whose owner filed nothing there becomes the pointing seat's finding. Number them F1…Fn. Nits skip the skeptic.

Done when: every non-nit finding has an F-number, a PR-added anchor and its lens tags.

### 5. Skeptics

Batches of about 8 findings, grouped by code region, one skeptic each, all in one concurrent batch, from [`SKEPTIC.md`](SKEPTIC.md).

Done when: every F-number has a verdict and a skeptic cite, or is marked not reached.

### 6. Grade

`block` → *Do before merge*. `fix` → *Do before merge*, or *Decide* when fix size or a judgement call makes a fast-follow honest. `question` → *Decide*. `verify` → *Verify in #N*. `nit` → Nits. FOLLOW-UP → the Follow-ups list (and an Open entry in the ledger). Apply verdicts per SKEPTIC.md § Chair's use, including the `block` guard and not-reached findings. A type change that fixes another finding goes into that card's Recommendation.

Done when: every survivor has a group or is a follow-up, and each *Do before merge* finding was re-read in source.

### 7. Write the page

Fill [`REPORT.html`](REPORT.html) into `~/.local/state/council/reports/<owner>-<repo>-<N>.html`, matching [`EXAMPLE.html`](EXAMPLE.html). [`FORMAT.md`](FORMAT.md) owns page order, card fields, drafts and language caps. Fill `<meta name="council">` for index.py, including `scope`, `lean` and `counts.followups`. Direction comes from the `design` lens's goal answer. Fill the Scope panel from the `shape` seat's Scope block. Cards still open from an earlier PR in the stack carry forward with a "from #M" tag. Choose each card's, nit's and follow-up's `data-cite`, then run `python3 lands.py <page>` to write every `a.lands` link from it. Never compute the path hash by hand.

Done when: the Scope panel is filled, every survivor is a card, follow-up or nit with head-SHA links, every card has both drafts and a Reply, and every card, follow-up and nit has a landing line in the PR diff linked from `a.lands` (FORMAT.md § Card).

### 8. Primer

The **tutor** ([`TUTOR.md`](TUTOR.md)) gets the page, clone, diff and spec, and returns at most three standalone concepts with the cards that assume each, or "no primer". Insert the Primer and the cards' `assumes:` links.

Done when: the Primer is in place (or omitted) and each concept is linked from a card.

### 9. Language checks

`python3 floor.py <page> --diff /tmp/<repo>-<N>/PR<N>.diff` → the **editor** ([`EDITOR.md`](EDITOR.md)), given only the page and FORMAT.md § Language and § Comments → apply its rewrites and supply every MISSING fact → the same `floor.py` run again.

Done when: floor.py passes and no MISSING remains.

### 10. Open and report

`open <page>`. In chat give only the direction, the scope verdict, counts by group (follow-ups included), card titles one line each under their group, and the path. With more than one PR: open `~/.local/state/council/reports/index.html` instead of each page, and give one table, one row per PR, with the columns PR · label · direction · scope · do · decide · verify · follow-ups · nits, then the index path.

Done when: the page is open and the report is in chat.

### 11. Ledger

Rewrite this stack's block: move answered entries to Closed in #N, add deferrals, follow-ups and separate ticket candidates as Open entries, record what was killed and why, and add a "Lens weights" line from the skeptics.

Done when: the ledger agrees with the page.
