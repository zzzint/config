---
alwaysApply: true
---

# Browsers

- Open browser tabs in Tern: `browser.open({ ..., app: { tern: true } })`, or pass no `app` option (Tern is the default).
- Never open a visible Chrome window: no `headed: true`, no `app: { tern: false }`, and no `app.path` pointing at a browser executable.
- When Tern can't host a tab, omp falls back to headless Chromium on its own. Let it.
- Playwright or Vitest browser runs inside a container or CI are headless and allowed.
