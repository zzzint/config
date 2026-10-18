---
name: council
description: Council review of an open PR or PR stack — parallel read-only seats, one per lens, skeptics that pressure-test every finding, and an editor that reads the result cold; the output is a local HTML review page of graded findings with concrete recommendations.
disable-model-invocation: true
---

Review a PR the way a **council** would: many independent seats each looking through one lens, a **skeptic** trying to knock down what each seat found, a chair who grades what survives, and an **editor** who reads the finished page knowing nothing else. The output is a review — facts and recommended changes — not a set of comments. The user decides what to do with it; this skill never writes to the PR.

Hard rules: every agent here is read-only (no edits, no git write commands, no installs, no test runs). A question answerable by reading more code is answered here, never handed to the user.

A **stack** is reviewed base → head, one PR per pass, carrying a **ledger** forward at `ledgers/<owner>-<repo>.md`. It opens with one line naming the stack order and which passes are done, then three sections, each entry one line with a `file:line` where one exists:

- `## Open entries (for #N)` — items the next PR must answer: verify-items the body deferred ("rides with #M"), consequences this pass could only trace so far, promises made to the user.
- `## Posted upstream` — comments the user has already posted on earlier PRs that later code could confirm, answer, or strengthen.
- `## Closed in #N` — entries answered in this pass, with the verdict and line, so the next pass never re-opens them.

Every entry moves from Open to Closed in the pass that can close it; the ledger, not the page, records each move.

## Process

### 1. Pin the PR and its context

Read the PR with `gh pr view <N> --repo <owner>/<repo> --comments` (or the host's PR reader): body, every review thread, every comment. Then:

- **Stack** — base/head, and what the body says "rides with" a later PR. Those are ledger items for *that* PR, not findings here.
- **Spec** — the design doc / PRD the PR implements. Doc↔code disagreement is a finding, including a doc merged earlier in the same stack.
- **Prior reviews** — threads already answered, so nothing is re-raised.
- **Ledger** — for a stacked PR, load [`ledgers/<owner>-<repo>.md`](ledgers/); each open entry goes to the seat whose lens owns it.

Clone the head branch shallow to `/tmp/<repo>-<N>`, save `gh pr diff <N> --repo <owner>/<repo>` beside it as `PR<N>.diff`, and record the head SHA (`git -C /tmp/<repo>-<N> rev-parse HEAD`) — every `file:line` on the page links to that commit. A depth-1 clone has no history; the diff is how every agent tells PR-added from pre-existing.

Done when: stack list, spec path, ledger entries, head SHA, and clone+diff exist.

### 2. Seat the council

Spawn every seat as a read-only sub-agent in **one concurrent batch**, using [`SEATS.md`](SEATS.md). Each seat receives the whole PR — never a module slice — plus its lens, the ledger entries its lens owns, and the shared context verbatim.

- **Standing seats**, always: premise · subtle bugs · types, abstractions & API ergonomics · overcomplication · security & tenancy · operational hardening · red team · spec & tests. A seat with nothing relevant says so in one line.
- **Elective seats**, as many as the chair judges this PR deserves depth on — each a specialist lens no standing seat holds, written for this change. `SEATS.md` lists lenses past PRs have earned as examples, not as the choices.
- A very large PR may split a seat by module; lens stays the primary axis.

While seats run, read the one change that would flip the verdict if it is wrong, so the chair holds an independent view.

Done when: every standing seat and each chosen elective is running.

### 3. Pressure-test

For each seat's report, spawn one **skeptic** (one concurrent batch, template in [`SKEPTIC.md`](SKEPTIC.md)). The skeptic's only job is to kill findings: pre-existing? deliberate and commented? enforced in another layer or the next PR? remedy actually correct? consumer-visible? worth the author's time? It returns per finding **uphold / demote / drop / escalate**, one line of reason, and its own line cite. Escalate is real — a skeptic that finds the consequence bigger than the seat saw raises the severity.

Done when: every finding carries a skeptic verdict and cite.

### 4. Grade and report

The chair:

- **Dedupes** across seats — one line flagged by two lenses is one card carrying both tags — and across the stack. A pointer ("see subtle bugs: file:line") whose owner filed nothing at that cite is promoted to a finding from the pointing seat's report and sent to a skeptic.
- **Maps** each survivor to a group — `block` → *Do before merge*; `fix` → *Do before merge* unless its judgement call or fix size makes a fast-follow honest, then *Decide*; `?` → *Decide*; `verify` → *Verify in #N*; no consequence anyone would see → Nits. The skeptic's verdict is final except for what lands in *Do before merge*, which the chair re-reads in source before it reaches the user. A type finding is mapped like any other; a type change that fixes another finding goes into that card's Recommendation.
- **Renders the page** from [`REPORT.html`](REPORT.html) — the review itself — to `reports/<owner>-<repo>-<N>.html` beside the ledgers, matching [`EXAMPLE.html`](EXAMPLE.html) and the order in [`FORMAT.md`](FORMAT.md) § Page: **High level context** (what the PR accomplishes, no judgement) → **Direction** (Yes / Maybe / No, from the premise seat) → **Primer** → **Cards** grouped *Do before merge* / *Decide* / *Verify in #N*, each with a coloured left bar, fix size, and any judgement call; cards open from an earlier page in a stack carried forward with their PR number → **Nits**. Card content follows `FORMAT.md` § Card. Every `file:line` links to the head-SHA blob on GitHub. One self-contained local file: inline CSS, no script, no external resources. No praise section, no stack-notes section, no actions list — the grouped cards are the to-do list.
- **Adds the Primer** — one sub-agent, the **tutor** ([`TUTOR.md`](TUTOR.md)), given the finished page, the clone, the spec, and the primer ledger `ledgers/<owner>-<repo>-primer.md`. It teaches only what a card on this page assumed, at most five concepts, links each to where it lives in the repo, and links back rather than re-teaching anything the ledger already holds. Its concept names are appended to the primer ledger with the PR number.
- **Runs the three language checks** in `FORMAT.md` § Language on the whole page, Primer included: the mechanical floor (`python3 floor.py <page>`), the **editor** (one sub-agent, [`EDITOR.md`](EDITOR.md), given the page and the rule and nothing else), then the chair's merge of its rewrites and missing facts. A page with any field the editor marked MISSING is not opened.
- **Opens it** for the user (`open <path>`) and **reports in chat** only the direction answer, the counts by group, the card titles as one line each under their group, and the file path.

The page recommends changes; it never drafts review comments. When the user asks for a comment on a specific card, draft it in chat per `FORMAT.md` § Comment voice.

Rewrite the ledger before moving on: close what this pass answered, add what it deferred, keep the rest — and record there what the page no longer carries: which findings the skeptics killed and why, and which ledger entries this pass closed. A single PR with no stack still writes one.

Done when: the page is open in front of the user, every card carries a concrete recommendation, every cite is linked, the editor's pass came back with no MISSING, and the Primer is on the page with its concepts recorded in the primer ledger.
