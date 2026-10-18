---
name: contextualize
description: Contextualize one thing in plain, followable language. Use when the user asks what something is, why it came up, whether it is related to the current work, or whether there is an ask for them; when they say a message was unclear or ask for it restated; and when introducing a finding, proposal, or change the user has not seen before.
---

One thing — usually a part of the assistant's last message, or something about to be introduced — is explained as if to a smart colleague who has not been following along. The output is a short, structured restatement. It adds no new work and drafts nothing.

## Resolve the reference first

When invoked by the user, the argument is a pointer, not a topic: "the tidy-up PR", "the second bullet", "that error.type thing". Find exactly what it points at in the recent conversation. When fired unprompted, the thing is whatever is about to be introduced; state it in the first heading and go on. If it fits two things, take the one in the assistant's most recent message and say in one line which was chosen. If it fits nothing, list the two or three nearest candidates in one line and stop there.

## Structure

Use these headings, in this order, each one to four short sentences. Omit a heading only when it is genuinely empty, and then say so in one word ("None.").

**What it is.** The thing, named as the code, docs, or tools name it. No review-coined shorthand, no roles the conversation assigned.

**Why it came up.** The observation or event that made it matter. Concrete: the number seen, the line read, the thing that failed.

**What it does or changes.** Behaviour, in the reader's terms: what a user, operator, or the next engineer would see differently.

**What it does not touch.** The nearest thing it could be confused with, and the boundary. This is where "is this about X or about Y?" gets answered before it is asked.

**How it relates to the current work.** One of: part of the current goal; adjacent and parked; unrelated and only noticed. Say which.

**Ask of you.** Either "None." or the one open decision, appended after this heading in the five-part shape the working agreement requires: **Decision**, **Context**, **Options**, **Recommendation**, **Question**. The Context part may be one line, since the sections above already carry it. One decision at most; a second one waits for its own message.

## Language

Plain, coherent, followable. The essence first — what this is and why it matters — and the details only after that is clear. A reader should get through it in one pass without stopping to reconstruct what a sentence meant.

Name things as the code, docs, and tools name them, in backticks. Prefer the number or the name that was seen over a characterization of it. Say "likely" where the truth is inferred rather than observed, and say what was observed.

## Example

Invocation: `/contextualize the storage filter fix`

**What it is.** A one-clause change to `filter/durable_object_storage` in `apps/otel-relay/collector-config.yaml`, the rule that drops Durable Object storage spans before they reach Dynatrace.

**Why it came up.** The rule kept a span only when its status was `ERROR`. Seven days of spans showed Cloudflare never sets that status on storage spans; the 115 failed `d1_run` spans carried the error in `error.type` with an empty status.

**What it does or changes.** A span is now dropped only when both signals are absent. A failed storage call keeps its span in the trace, which is what the rule's comment and the PR body had promised.

**What it does not touch.** Which spans Cloudflare emits, the export volume of anything other than storage spans, and the status check itself, which stays for the case where Cloudflare adopts the standard signal.

**How it relates to the current work.** Part of the current goal: it shipped in #308 and is live on staging, dev, and test.

**Ask of you.** None.
