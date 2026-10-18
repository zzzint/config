---
name: walkthrough
description: Walk the user through how one path in a system actually works, start to finish, in plain, followable language. Use when the user asks "how does X work", "walk me through", "what happens when", "trace this", or needs to reason about code they did not write; and before proposing a change to a path the user has not seen end to end.
---

One path through a system — a request, a document, a job, a value — is followed from where it starts to where it ends, for a smart colleague who knows how software works but not how this system works. The output is a short sequence of steps, each grounded in the code. It adds no new work, proposes no changes, and drafts nothing.

## Resolve the path first

The argument names a path, not a topic: "an order from checkout to the warehouse", "what happens when a user deletes their account", "how a webhook gets retried". Pin down three things before tracing: the starting event, the end state, and which branch to follow when the path splits. If the argument leaves one of those open, pick the most common case, say in one line which was chosen, and go on. If the argument fits no path you can find, name the two or three nearest candidates in one line and stop.

## Trace before writing

Read the code along the path. Do not reconstruct it from file names, docs, or memory. Docs describe what was intended and drift. When the docs and the code disagree, the walkthrough follows the code and says where they disagree. A step you could not trace — a dynamic dispatch, a binding resolved at runtime, a service you cannot see into — is shown as a step anyway, marked as not traced, with what was observed on either side of it.

## Structure

**The path in one sentence.** Where it starts, where it ends, and what it produces.

**Steps.** Numbered, one short paragraph each. Each step says:
- what happens, in domain terms first and mechanism second;
- where it lives, as `path/to/file.ts:line` or the symbol name;
- what crosses into the next step — the identifiers, the data shape, the side effect.

Mark a step where something durable happens — a write, a message sent, a model called, money or data leaving the system — because those are the steps a change has to respect.

Aim for five to twelve steps. Fewer and the walkthrough is hiding the interesting part; more and it is narrating lines. Collapse plumbing into the step it serves.

**Where it can go wrong.** Up to four places on the path where a failure, retry, partial state, or surprising behaviour lives. Each one names the step number and what the reader would see.

**What it does not cover.** The neighbouring paths and branches deliberately left out, so the reader knows where to look next.

## Language

Plain, coherent, followable. A reader should be able to get through the steps once, in order, and come out able to predict what the system does. Use the project's own vocabulary — its glossary, if it has one — and name code as the code names it, in backticks. Prefer what the code does over what a function's name suggests. Say "likely" where a step is inferred rather than read.

Do not explain general programming. Do explain anything this system does differently from how a reader would assume it works.

## Example

Invocation: `/walkthrough what happens when a user resets their password`

**The path in one sentence.** A user submits their email on the reset form, and it ends with a new password hash stored and every existing session for that account signed out.

**Steps.**
1. The form posts the email to `POST /password/reset`. The handler returns the same "check your email" page whether or not the account exists, so the endpoint cannot be used to discover accounts. *(`src/routes/password.ts:22`)*
2. **Durable:** if the account exists, `createResetToken` generates a random token and stores only its hash in `password_resets`, with a 30-minute expiry. *(`src/auth/reset.ts:14`)*
3. **Durable:** the mailer queues an email with a link containing the raw token. This is the only place the raw token leaves the system.
4. The user opens the link. `GET /password/reset/:token` hashes the token, looks it up, and shows the new-password form if it is unexpired and unused.
5. The user submits a new password. The handler checks the token again — the form may have sat open past the expiry — then hashes the password.
6. **Durable:** in one transaction, the new hash is written, the reset row is marked used, and every row in `sessions` for the account is deleted. *(`src/auth/reset.ts:51`)*
7. The user is redirected to the sign-in page; they are not signed in automatically.

**Where it can go wrong.**
- Step 3: if the mail queue is down, the user still sees the success page and no email arrives; nothing tells them.
- Step 5: two tabs submitting the same token both pass the check; the transaction in step 6 lets only the first one win.

**What it does not cover.** Changing a password while signed in, and resets started by an administrator, which take separate paths.

*(Illustrative: file names and line numbers stand in for what a real walkthrough would cite.)*
