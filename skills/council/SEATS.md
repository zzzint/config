# Seats

Spawn all seats in one concurrent batch of read-only sub-agents (whatever the host calls them). Every seat receives the shared context verbatim plus its own lens block.

## Shared context (verbatim skeleton)

```
# Goal
Council review of PR #<N> in <owner>/<repo>: <one-line summary>. Branch checked out READ-ONLY at /tmp/<repo>-<N>; the PR's own diff is at /tmp/<repo>-<N>/PR<N>.diff — grep it to tell PR-added lines from pre-existing code (depth-1 clone, git history is useless). <Review state: none yet | prior threads already answered: list them so nothing is re-raised.>

# Spec
<design doc / PRD path> — treat as the spec; code/spec disagreement is a finding.

# Constraints
- READ-ONLY. Never edit files, never run any git write command, never run installs or tests. Evidence is from reading code.
- You hold ONE lens (below). Report only through it; another seat owns the rest. Do not report style.
- Ownership, so the same line is filed once: a race, window, or check-then-act belongs to **subtle bugs** (or the concurrency elective when seated) — every other seat that notices one writes a single line "see subtle bugs: <file:line>" and moves on. Authz, scoping, and input bounds belong to **security**; failure modes, idempotency, and telemetry to **operational hardening**; doc↔code drift to **spec & tests**. Red team reports the abuse *sequence*, and hands the underlying defect to its owner by cite rather than refiling it.
- Each finding: severity — one of `block` · `fix` · `question` · `verify` (depends on a later PR in the stack) · `nit` (true, no consequence anyone would see) · one-line claim · file:line evidence · 1–2 plain sentences on why it matters to a user or operator · the remedy you would propose. Rank them. Nothing relevant → one line saying so.
- A claim you can verify by reading more code MUST be verified, not posed as a question.

# Contract
Final report: ranked findings; explicit PASS/FAIL on every checklist item; one paragraph on what you read fully vs skimmed.
```

## Per-seat block

```
# Lens
<one of the lenses below, verbatim>
# Checklist (explicit PASS/FAIL each)
1. <spec rule this lens owns>
2. <ledger entry from the previous stack pass this lens can close>
…
```

## Standing seats

**Subtle bugs.** Control flow that passes tests: stale in-memory state written back over a fresher row; check-then-act without atomicity; cancel/timeout windows between the last check and the final write; recovery or dedupe rules that match on the wrong key (name vs id, index vs key); null paths; off-by-one on caps and pagination; error paths that swallow and return partial data as success; the same rule implemented twice that will drift.

**Types, abstractions & API ergonomics.** In the reviewer's priority order:
1. *Stringly-typed identities* — bare `string` ids where a swap is a tenant/agent/run bug; adjacent same-typed params; composite keys built by concatenation. Remedy: branded ids (zod `.brand<"X">()` at the parse boundary), object params.
2. *States that exclude each other as optional-field bags* — success / failure / infra-failure in one shape; `passed: true` alongside an `error` representable. Remedy: `kind`-discriminated unions; consumers switch exhaustively.
3. *Parse once at the boundary* — parsed input re-narrowed deep inside (`typeof`, `isPlainObject`, `as`, `!`); `JsonValue` blobs where a schema for that value already exists nearby. Locate the casts that matter.
4. *Boolean/optional soup vs named modes* — `f(a?, b?, force?)` where a union of modes makes the wrong call unrepresentable and retires a silent precedence rule.
5. *Return types* — the same wide type for success and failure; result unions that dissolve into a record one layer down.
6. *Known-key vocabularies typed as open records* — a `const` tuple of keys defined and unused by the schema beside it; passthrough wire types with no strict authoring type.
7. *Generics* inferring from arguments that would delete casts at call sites.
8. *Seams* — transport/repository interfaces: precise per-method result types, or wide unknowns the caller re-checks; barrels leaking internals.
9. *Abstraction fit* — one responsibility per module; pure-engine vs transport split honoured; parallel arrays where a keyed structure fits; a mutable `Partial<Record>` handle where phase-specific commands would make a race unwritable.
10. *API ergonomics* — read every new exported function, method, and request shape from the caller's side: does inference and completion steer toward the right call, or must the caller spell out type parameters, remember an argument order, or know a precedence rule? Is the wrong call a compile error or a runtime surprise? Does the return type narrow to what was passed? Would a first-time caller reach for it without reading the implementation? Name the call site where a plausible mistake compiles.
Output: each as a finding in the shared shape — severity, claim, cite, why it matters, and a **sketched better shape** as the remedy, stating what the change costs now versus after it has consumers. When a type change is the fix for something another seat will have found (a race, a state bag), say so by cite so the chair can merge it into that card. Then a short list of genuinely good decisions.

**Overcomplication.** What the diff builds that the problem did not ask for: an abstraction with one caller; a config knob, mode, or flag nothing sets; a layer that forwards to another layer unchanged; a generic where two concrete lines would do; a bespoke helper beside a library or an existing helper that already does it; a "for later" seam, alias, or compatibility path with no present consumer; prose (comments, docs, PR body) longer than the behavior it describes. For each: what the simpler shape is, and what it would cost to switch now versus after it has consumers. Complexity the spec demands is not a finding; say so once.

**Premise.** Whether the work should exist in this shape at all, judged before the code is judged. This is the one seat that reads the PR body — for the *why* it states, never to check its claims of what was done. Read that motivation, the linked ticket or spec, and what the codebase already does; then answer, with cites: Is the problem real, and is it the problem the diff solves — or does the diff solve a nearby, easier one? Does something already in the repo do this (a helper, a route, a package, a pattern) that the PR re-implements or bypasses? Is this the right layer — is a concern being solved in a service that another service already owns, or at the edge when it belongs in the domain, or in code when it belongs in configuration or process? Is the scope right — does the diff carry work the motivation does not call for, or omit work it does? Is there a simpler design that meets the same motivation, and what would it cost to switch now? A finding here is the most expensive kind to discover late, so it leads the report when it survives; a premise that holds gets one sentence saying why, not silence.

**Security & tenancy.** Every read and write scoped from signed/verified context, never from body or query; any UPDATE/DELETE keyed by id alone; lookups by a child id that skip the parent scope; privilege grants (roles, service principals) and the condition that gates them; input bounds on every accepted shape (strings, arrays, JSON breadth, regex patterns); injection surfaces where external text reaches a prompt, a query, or a shell; secrets or upstream exception text echoed into responses or persisted rows; scripts that sign privileged requests against a configurable target.

**Operational hardening.** What happens when a dependency is down, slow, or returns garbage; idempotency of anything a cron, retry, or duplicate request can fire twice; cancel and timeout coverage across every phase; migrations — additive or not, rollback story, existing-row rewrites; load and cost bounds — per-tenant, cross-tenant, cross-agent; telemetry and alerting on *every* terminal path including the exception path; cleanup of what smoke scripts and jobs create.

**Red team.** Adversarial: how would I abuse, exhaust, or mislead this — as an authenticated operator, as a tenant, as poisoned upstream data, as a colliding concurrent caller, as a script pointed at the wrong environment. Each finding is a concrete sequence of steps and the line that lets it happen.

**Spec & tests.** Doc↔code drift line by line, including a doc merged earlier in the stack that this PR's code now contradicts; tests that assert the implementation's own choice (a test pinning a bug as intended, a fake echoed back, a string compared to itself); a "regression test" that never exercises the failing path; coverage gaps precisely where the other seats' findings sit.

## Elective seats

The chair decides what this PR deserves depth on, and how many seats that takes. Read the diff, ask "what would a specialist in X find that no standing seat is looking for?", and seat each of those specialists — written in the same shape as the standing lenses, specific to this change. Examples of lenses past PRs have earned, not a menu to choose from:

- **Data model & migrations** — schema vs doc; every index a repository query needs; codecs parsing through the schema that already exists; malformed-row behavior.
- **Concurrency** — every check-then-act; every "coalesce / dedupe / once per X" promise vs the store's actual uniqueness guarantees.
- **API compatibility** — wire shape changes vs existing callers; verb semantics (PUT vs PATCH); error codes stable.
- **UI & accessibility** — states rendered (loading, empty, error, partial), keyboard and ARIA, copy that reads raw error text.
- **Performance** — N+1, unbounded scans, payload caps, hot-path allocations.
- **i18n** — hardcoded strings, plural concatenation, locale coverage.
- **Dependency & supply chain** — new packages, lockfile drift, pinned versions.
- **Docs & DX** — runbooks runnable as written; env vars documented; local testing guide true.
