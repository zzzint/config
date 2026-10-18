---
name: no-silent-workflow-fallback
description: "Surface blockers instead of silently replacing an agreed execution mode"
condition: "Falling back to OMP(?:’|')s isolated subagent orchestration"
scope: "text"
---

The agreed execution mode is blocked. Do **not** substitute another mode or workaround. Stop before dispatching work and surface the blocker with full context: what was agreed, what failed, what remains unaffected, and the concrete choices for resolving it. Recommend one option and ask the user to choose.