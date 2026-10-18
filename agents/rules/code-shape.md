---
name: code-shape
description: "How code should be shaped and typed — fires when editing or writing a source file"
condition: ["*.ts", "*.tsx", "*.js", "*.jsx", "*.py", "*.go", "*.rs", "*.rb", "*.java", "*.kt", "*.swift", "*.c", "*.h", "*.cpp", "*.cs", "*.php", "*.sql"]
interruptMode: "tool-only"
---

# How this code should be shaped

Code gets read far more often than it gets written, and what makes it costly to
read is how much has to be held in mind at once. Everything here is that one idea
wearing different clothes.

A function's name should be a sentence with no "and" in it. If naming it honestly
needs a conjunction, it is two functions.

Keep working out what to do apart from doing it. The part that decides what
something means should be readable, and testable, without a database, a terminal,
or a network. Put the effects in a thin shell around it.

Hand a function what it needs instead of letting it go and fetch. Rendering that
queries, or a calculation that reads a file, cannot be read or tested without
standing up the thing it reaches for.

Let the control flow follow the data. A closed set of cases deserves one function
that covers all of them, with a guard that fails to compile when a new case
appears — not a chain of conditionals that happens to cover today's. A trailing
`else`, or a comment naming the cases it quietly absorbs, is a decision nobody
made, and it stops being right the moment someone adds a case.

Never branch on what is shown on screen. Menu labels, emoji, and human-readable
strings get changed for cosmetic reasons, and a comparison against one fails
silently the moment it drifts from the copy that produced it.

Say each thing once. The same sentence at five call sites is five chances for four
of them to drift apart.

Name what came back instead of flagging it. A `boolean` whose `false` means
"someone revised this while you were reading it" sends every reader off to look it
up. One trap when fixing that: swapping a boolean for a string union compiles
clean while silently breaking every `if (f())` that calls it, because a non-empty
string is always true and no typechecker will mention it.

Derive instead of restating. A second union written by hand drifts from the first;
one defined by `Exclude` from the other cannot.

# Types

Shape types so the wrong thing cannot be written down. Use a union of cases when
only one can be true at a time. Brand identifiers that must never be swapped for
each other. Handle every case of a union explicitly.

Do not widen a known, closed set to `string` because it is convenient. Do not pass
a domain identifier as a bare number.

Parse anything untrusted once, at the edge, into the precise type the rest of the
code expects. Everything past that point should be able to assume it is already
right.

Where a vocabulary belongs to something else — an external schema, an API, a data
file — generate the type from that source. Do not copy it by hand.

# Comments

Comments explain the constraints and boundaries that the code cannot say for
itself. Where a rule exists because something went wrong, write the failure down
next to it: a bare constraint reads as arbitrary, and the next person tidying up
deletes it.

Do not narrate what the code does, list who calls it, or restate its own name.
