# Settings and prompts

My editor settings and the instructions I give coding agents.

- `agents/AGENTS.md` — my system-wide working agreement for agents. Lives at
  `~/.omp/agent/AGENTS.md`.
- `agents/rules/` — rules loaded alongside it. Live in `~/.omp/agent/rules/`.
- `skills/` — my own skills. Live in `~/.agents/skills/`.
  - `brief`, `compare`, `contextualize`, `handoff`, `walkthrough` — plain-language
    explanations of work in progress.
  - `council` — multi-agent PR review that renders an HTML page. Needs `gh` and
    `python3`. Its `ledgers/` and `reports/` are per-machine history and are not
    kept here.
  - `ui-charcuterie` — rounds of divergent Storybook prototypes. Needs no other
    skill, but relies on omp's harness (`task` with `outputSchema`, `browser`,
    `local://`, `skill://`) and a Storybook app.
- `zed/keymap.json` — Zed key bindings. Lives at `~/.config/zed/keymap.json`.

These are copies. Edit the live file, then copy it back here.
