# council — a PR review skill

Drop this folder at `~/.agents/skills/council/` on the target machine (and symlink
`~/.claude/skills/council -> ../../.agents/skills/council` if Claude Code should see it).
Needs `gh` (authenticated) and `python3`. Invoke as `/council <PR url>`.

The skill creates `ledgers/` and `reports/` beside these files as it runs; they are the reviewing
machine's own history and are not part of the package.
