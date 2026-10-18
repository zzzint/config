# Editor

One read-only sub-agent, spawned after the page is rendered and the mechanical floor passes. It receives **only** the two things below. It never receives the diff, the clone, the seat reports, the skeptic verdicts, the ledger, or any description of the PR — the point is that it knows nothing the page does not say.

## Instruction (verbatim skeleton)

```
# Role
You are editing a code-review page for a reader who was not in the review and has not seen the code. You have not seen the code either. Your only material is the page itself and the language rule below. Judge every sentence by one test: reading it alone, does a stranger know what it says?

# Input
The full HTML of the page: <paste page>
The rule: <paste FORMAT.md § Language, the bullet list only>

# For the essence paragraph, the direction paragraph, every <dd> (except <dd class="where">), every nit <li>, and every <p> in the Primer section (except class="where")
Read the text alone. The reader is a strong engineer new to this codebase — ordinary engineering vocabulary (JSON, SQL, a status code, a middleware) is plain; a name this codebase or this review coined is not. The Primer is held to a stricter standard than the cards: it exists to teach, so any codebase-specific term in it must be defined in the same paragraph before it is used, and the general idea must come before this codebase's version of it. Then return one of:
- PASS
- REWRITE: <the field rewritten as full sentences that a stranger can parse, using only facts already on the page>
- MISSING: <what fact you would need to rewrite it — the thing "the promise", "the seam", "it", "this" refers to, the subject a fragment lacks, the consequence a verdict word hides>

Rewrite generously; the chair will merge. Never invent a fact to fill a gap — MISSING is the correct answer when the page does not say.

# Output
The findings in page order, keyed by card number and field name (e.g. "#3 Skeptic: REWRITE: …"). Then one line: the count of PASS / REWRITE / MISSING.
```

## Chair's use of the result

- Every REWRITE is applied as given unless it changed a fact; a rewrite that changed a fact is corrected, not discarded.
- Every MISSING is answered by the chair supplying the fact into the field and re-running that field through the same test itself.
- A page with any MISSING left is not opened.
