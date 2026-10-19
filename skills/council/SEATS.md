# Seats

All seats run in one concurrent batch of read-only sub-agents. Each gets the shared context verbatim plus its seat block.

## Shared context (verbatim skeleton)

```
# Goal
Council review of PR #<N> in <owner>/<repo>: <one-line summary>. Head checked out READ-ONLY at /tmp/<repo>-<N>, with history (git log and blame work). The PR's diff is /tmp/<repo>-<N>/PR<N>.diff. <Answered threads, never re-raised: list | none.>

# Spec
<design doc / PRD path | none>. Code/spec disagreement is a finding.

# Constraints
- READ-ONLY: no edits, no git write commands, no installs, no tests. Evidence comes from reading code.
- You hold ONE lens (below). Report only through it. No style findings.
- Ownership, so a line is filed once: goal, layer, ownership, alternatives and hard-to-reverse commitments → design. Races and check-then-act → correctness. Authz, scoping, input bounds, failure modes, idempotency, telemetry → safety. Doc/spec drift → shape. For another lens's issue write one line "see <lens>: <file:line>". A type change that would fix another lens's finding → types files it, citing that line.
- A claim you can check by reading more code MUST be checked, not posed as a question.
- Nothing relevant → one line saying so.

# Finding shape (ranked)
severity: block | fix | question | verify (a later stack PR settles it) | nit (true, no consequence anyone would see)
claim: one line
cite: file:line
anchor: PR<N>.diff:<line> of a PR-added line, or "pre-existing"
why: ≤2 sentences, in user or operator terms
remedy: the named move, then the smallest change

# Report
Ranked findings. PASS/FAIL per checklist item. One paragraph: what you read fully vs skimmed.
```

## Seat block

```
# Lens
<one lens below, verbatim>
# Checklist (PASS/FAIL each)
1. <spec rule this lens owns>
2. <ledger entry this lens can close>
…
```

## Standing lenses

**`design`** — architecture and goals: does this move the system where it needs to go? Read the PR body and linked ticket for the goal, then `docs/architecture/`, the ADRs, the roadmap and the code this touches. Think before filing. The best finding here is often one well-aimed question.
- *Goal* — what is this for? Is the problem real, and is it the one the diff solves, or a nearby easier one? A goal that holds gets one sentence why. This sets the page's Direction.
- *Fit* — which service or package owns this concept? Does the change keep it there, keep dependencies pointing the right way, and avoid a second way to do what the repo already does?
- *Commitments* — what becomes hard to reverse: a public API or wire shape, stored data, a migration, a contract others build on. Is it made on purpose, and recorded in an ADR when it is a decision?
- *Alternatives* — at least one materially different design (another layer, another owner, config instead of code, doing less), with its cost now versus after consumers exist. File it only when it is cheaper or safer. Otherwise say in one sentence why the chosen design wins.
- *Trajectory* — the next planned steps (later stack PRs, the ticket, the roadmap, ADRs). Does this make them easier or harder? Does it contradict a recorded decision?

One structural problem is the review: lead with it, and drop the smaller items it explains. Findings here are usually `question`: the move and its tradeoff, not an edit.

**`shape`** — the size and simplicity of what was built. Read the PR body for its motivation, not to check its claims.
- *Overcomplication* — an abstraction with one caller; a knob nothing sets; a layer that forwards unchanged; a generic where two concrete lines would do; a bespoke helper beside a library or existing one; a "for later" seam or alias with no consumer; prose longer than the behavior.
- *Scope* — over ~1000 changed lines, or refactor mixed with feature → suggest a split along a named seam. Work the motivation does not ask for, or asks for and is missing.
- *Drift* — doc↔code and spec↔code, line by line, including docs earlier in the stack. Runbooks runnable as written; new env vars documented.

Name the move: replace conditionals with a typed model, collapse duplicate branches, separate orchestration from logic, reuse the canonical helper, delete a pass-through wrapper. Moving logic to the package that owns it is `design`'s Fit. Give the cost now versus after it has consumers. Not findings: a helper that names a concept, merging unrelated logic to look simpler, complexity the spec demands.

**`correctness`** — code that passes tests and fails in use.
- *Bugs* — stale in-memory state written over a fresher row; check-then-act without atomicity; cancel or timeout windows before the final write; recovery or dedupe on the wrong key (name vs id); null paths; off-by-one on caps and pagination; swallowed errors returning partial data as success; one rule implemented twice.
- *Tests* — a regression test that never runs the failing path; a test pinning the implementation's own choice (a bug as intended, a fake echoed back); coverage gaps on the riskiest new branches and where your findings sit.

**`types`** — types, abstractions and API ergonomics, in priority order:
1. *Stringly ids* — bare `string` ids a swap turns into a tenant bug; adjacent same-typed params; concatenated keys → branded ids at the parse boundary (zod `.brand<"X">()`), object params.
2. *Exclusive states as optional bags* (`passed: true` beside an `error`) → a `kind`-discriminated union, switched exhaustively.
3. *Parse once at the boundary* — re-narrowing deep inside (`typeof`, `as`, `!`); `JsonValue` where a schema exists nearby. Name the casts that matter.
4. *Boolean soup* — `f(a?, b?, force?)` with a silent precedence rule → a union of named modes.
5. *Return types* — one wide type for success and failure; result unions that dissolve a layer down.
6. *Known keys as open records* — a `const` key tuple the schema ignores; wire types with no strict authoring type.
7. *Generics* that would infer from arguments and delete call-site casts.
8. *Seams* — interfaces with precise per-method results, or wide unknowns callers re-check; barrels leaking internals.
9. *Abstraction fit* — one job per module; engine split from transport; parallel arrays where a keyed structure fits; a mutable `Partial<Record>` where phase-specific commands would make a race unwritable.
10. *Ergonomics from the caller's side* — does inference steer to the right call, or must callers spell type parameters, recall argument order, know a precedence rule? Does the return narrow to what was passed? Name the call site where a plausible mistake compiles.

Remedy: a sketched better shape, with its cost now versus after it has consumers. A shape that makes a wrong call or invalid state unwritable earns a finding; a rename is a nit.

**`safety`** — security, abuse and operations.
- *Security & tenancy* — reads and writes scoped from verified context, never body or query; UPDATE/DELETE by id alone; child-id lookups skipping the parent scope; privilege grants and their gate; input bounds on every shape (strings, arrays, JSON breadth, regex); injection into a prompt, query or shell; secrets or upstream error text in responses or rows; scripts signing privileged requests at a configurable target.
- *Red team* — abuse, exhaust or mislead it as an operator, a tenant, poisoned upstream data, a colliding concurrent caller, a script aimed at the wrong environment. File each as a concrete sequence of steps and the line that allows it. A race inside it → point at correctness.
- *Operations* — dependency down, slow or returning garbage; idempotency under cron, retry or duplicate requests; cancel and timeout in every phase; migrations (additive, rollback, row rewrites); deploy order; load and cost bounds per tenant and across tenants; telemetry on every terminal path, exceptions included; cleanup of what scripts create; new packages and lockfile drift.

## Electives

Full tier only. Ask "what would a specialist in X find that no standing lens covers?" and write that lens in the same shape for this change, with a short tag name. An elective that takes over a standing topic (concurrency takes races) says so in both seat blocks. Examples, not a menu: **data model** (schema vs doc, an index per query, malformed rows), **concurrency** ("once per X" promises vs real uniqueness), **API compatibility** (wire shape vs callers, stable error codes), **UI** (empty/error states, keyboard, ARIA), **performance** (N+1, unbounded scans, payload caps).
