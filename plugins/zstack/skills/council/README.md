# council — a PR review skill

Ships in the `zstack` plugin (`omp plugin install zstack@zzzint`). Needs `gh` (authenticated) and `python3`.

- `/skill:council <owner>/<repo>#<N>` reviews one PR; a list of PRs is reviewed as a stack, base to head.
- `/skill:council` with no PR reviews every open PR where you are a requested reviewer.

Each PR gets one local HTML page with graded cards. Every card carries two comment drafts, one that
asks and one that says it directly, linked to the diff line it would land on. Pick, edit and copy
them on the page; the skill never writes to the PR. A run over more than one PR also builds an
index page.

| File | Role |
|---|---|
| `SKILL.md` | The process, step by step |
| `SEATS.md`, `SKEPTIC.md`, `TUTOR.md`, `EDITOR.md` | Instructions for the sub-agents |
| `FORMAT.md` | Page layout, card fields, comment voice, language rules |
| `REPORT.html` | The page template |
| `floor.py` | Mechanical language and anchor checks for a page |
| `lands.py` | Writes each comment's diff link from the line it lands on |
| `index.py` | Builds `~/.local/state/council/reports/index.html` from every page |
| `EXAMPLE.html`, `EXAMPLE.diff` | A made-up review to match; `python3 floor.py EXAMPLE.html --diff EXAMPLE.diff` passes |

The skill writes `ledgers/` and `reports/` under `~/.local/state/council/`, never beside these files,
because a plugin upgrade replaces this folder. They are the reviewing machine's own history, can
quote private repositories, and are not part of the package.
