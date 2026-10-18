---
name: charcuterie
description: Storybook charcuterie board — rounds of divergent UI prototypes, one sub-agent each, narrowed by user feedback until the user picks a winner.
disable-model-invocation: true
---

Run a **board**: rounds of small, meaningfully different Storybook prototypes of one concept, each authored by its own sub-agent, narrowed by the user's reactions until the user names a winner. **Divergence** is the product: every item on a round must be a different *approach*, not a variant of a neighbour.

A sub-agent that reads this file follows [`prototyper.md`](prototyper.md) only; this loop belongs to the parent.

The concept arrives as the invocation's `User:` text. When it is missing, ask for it before Setup.

## Board file

`local://charcuterie-<concept>.md` (kebab-case concept) is the single source of truth for the run. Create it in Setup; update it at the end of every step that changes it. It holds:

- **Env**: target tree, app directory, board root, Storybook base URL, how it runs (host / devcontainer + config path + container id), and `startedBySkill: yes|no`.
- **Items**: one row per item — global number (`#1`… continuing across rounds; never reset), round, title, thesis, traits, origin (`card: <direction>` or `wildcard: <seed A> + <seed B>`), story id, user verdict.
- **Keep** and **Drop**: trait lists distilled from the user's reactions.
- **Backlog**: the open topics the user's feedback has raised, most important first. Each round works on exactly one.
- **Decisions**: behaviour the user has settled (semantics, constraints) that every later item must honour.
- **Taken directions**: one line per item ever built.

## 1. Setup

1. Resolve the **target tree**: `git rev-parse --show-toplevel` from the session directory. All board files are written under it.
2. Find the Storybook app inside the target tree: `glob **/.storybook/main.*` (respect gitignore). More than one → ask which app. Read `main.*` for the `stories` setting and framework, and read two existing `*.stories.*` files for conventions (meta shape, decorators, providers, fixtures).
3. Choose the **board root**: a folder under the app, default `src/charcuterie`, such that a full generated path — `<board root>/<concept>/round-1/Example.stories.tsx` — matches the `stories` setting. No folder qualifies without a config edit → stop and tell the user which `stories` entry is missing.
4. Find a running Storybook **for the target tree**. Tree identity comes from where the server runs, never from `index.json` (its `importPath`s are relative and exist in every worktree). A server belongs to the target tree only on an exact match: `git -C <hub describe cwd> rev-parse --show-toplevel` equals the target tree, or its devcontainer's `devcontainer.local_folder` label equals the target tree (`docker ps --filter label=devcontainer.local_folder=<tree> --format '{{.ID}} {{.Ports}}'`). Nested worktrees (e.g. `.claude/worktrees/*`) are separate trees. Then confirm the base URL answers `<base>/index.json` — an open port alone proves nothing, since another process may squat it. A live Storybook that belongs to a different tree → ask the user which tree to use.
5. None for the target tree → start one with `hub` `op:"start"`, `ready.log: "Local:"` plus `ready.port`:
   - Repo has `.devcontainer/` → run inside it (`npx -y @devcontainers/cli up`, then `… exec … storybook dev -p 6006 --exact-port --host 0.0.0.0 --no-open --ci`). Export `CHOKIDAR_USEPOLLING=true`: bind-mounted edits from the host are otherwise invisible to the watcher. If the container publishes no Storybook port, write an untracked override `.devcontainer/<name>/devcontainer.json` (copy of the base with `appPort: ["<free host port>:6006"]`; `dockerfile` path relative to the new folder; in a git worktree, also bind-mount the main repo's `.git` at its host path) and recreate the container. Pick a host port nothing listens on.
   - Otherwise run the app's Storybook binary on the host.
   - Record `startedBySkill: yes`.
6. Restarting later: `hub stop`/`restart` leaves the in-container Storybook alive, still holding the port with a stale index. Kill the container's `storybook dev` process (`docker exec <id> ps` / `kill <pid>`) before starting again.

7. Build the **shared base** in `<board root>/<concept>/_shared/` before the first round, and extend it when a focus needs more:
   - a data corpus (realistic, long, unique content, including the edge states the concept has);
   - a scaffold that composes the app's real components and styling, with a slot for each part a focus might vary;
   - a `Baseline` story, titled `Charcuterie/<Concept>/_Shared/Baseline`.

   Prototypers import it and never edit it, so items differ only in the round's focus and stay comparable. Delegate the build if it's large, then run the Look check (step 3) on the Baseline yourself before any round uses it.

**Done:** a Storybook identified as the target tree's answers `<base>/index.json`, the board root is covered by the `stories` setting, the board file exists with Env filled in, and the Baseline story has passed your Look check.

## 2. Plan a round

Board size is **8** unless the user asked for another number this round.

- **Round 1**: write **direction cards** for half the items (the strongest obvious approaches, each a one-line thesis distinct from the others). The rest are **wildcards**.
- **Later rounds**: at least ⅓ wildcards. Every other item is a **recombination** card: a thesis built from named Keep traits. Spread Keep traits so each appears in at least one item, and pair traits that never shared an item before.
- **Wildcard draw**: for each wildcard, draw from [`seeds.md`](seeds.md) with real randomness: `sort -R` over `skill://charcuterie/seeds.md`, skip `#` lines, take the first two lines whose categories differ. Redraw when that pair already appeared this round. Pass the two seed lines verbatim; the sub-agent invents the direction.
- **One focus per round**: each round explores exactly one topic from the Backlog: the one the user names, or else the top one. All items vary that focus and keep everything else at the Baseline. When feedback raises new topics, add them to the Backlog instead of widening the round.
- **Behaviour focus**: when the user's complaint is about *how something behaves* (jumping, alignment, sync), not how it looks, first build the mechanics once in the shared base with a debug harness story. Verify it yourself with numeric checks (per-case pass counts, pixel deltas). Then have every item use it and vary only the presentation. In Look, re-run the same numeric checks on every item, not just screenshots.

Assign each item a global number, a PascalCase item name, its file `<board root>/<concept>/round-<N>/<Item>.stories.tsx`, and story title `Charcuterie/<Concept>/Round <N>/<Item>`.

**Done:** every item has a number, name, file path, title, and either a card thesis or two seed lines; recombination cards each cite the Keep traits they carry.

## 3. Build the round

Dispatch one `task` batch with one item per board item (default `task` agent). Shared `context` carries: the concept, the target tree, app directory and Storybook base URL, the conventions read in Setup (paths to the two example stories and any fixture modules), the Keep / Drop lists, and **every taken direction** — prior rounds plus every card in this round, each labelled with its item number — so parallel sub-agents steer apart. Each item's `task` says: read `skill://charcuterie/prototyper.md` and follow it; then its number, name, file path, title, and card thesis or seed lines. When `skill://charcuterie` does not resolve yet (the skill was installed this session and not reloaded), point sub-agents at the brief's absolute path under the skill directory instead.

Set this `outputSchema` on every item:

```json
{"type":"object","properties":{
  "title":{"type":"string"},
  "thesis":{"type":"string"},
  "traits":{"type":"array","items":{"type":"string"}},
  "file":{"type":"string"},
  "storyIds":{"type":"array","items":{"type":"string"}},
  "smoke":{"enum":["pass","fail"]},
  "notes":{"type":"string"}},
 "required":["title","thesis","traits","file","storyIds","smoke","notes"]}
```

Then verify, in order:

1. **Index**: every returned `storyIds` entry appears in `<base>/index.json`.
2. **Look**: use every story the way the user will; a static screenshot misses broken scrolling and broken transitions.
   - Open it, including its About page.
   - Scroll its scroll areas end to end, and confirm nothing jumps and the page itself doesn't scroll.
   - Perform every interaction its About page lists.
   - For motion, run the full round trip (open, then close), capturing frames mid-transition both ways.
   - Screenshot after each step, in both themes.

   An item with overlapping or clipped elements, large dead regions, dead controls, broken scrolling, a transition that doesn't match its About page, or styling that departs from the Baseline outside the round's focus is **undercooked**.
3. **Divergence**: compare every item's returned thesis and traits against every other item this round. Two items **collide** when their overall approach is substantially the same; a shared Keep trait or one shared dimension is expected and is not a collision. Separately, flag any item carrying a Drop trait.
4. **Rework**: each item that failed smoke, is missing from the index, is undercooked, collides, or carries a Drop trait gets one pass via `hub send` to its agent — for undercooked, name what you saw; for a collision, include the other item's returned thesis and ask it to move away; for a Drop trait, name the trait to remove. Re-check what came back; still broken or undercooked → mark `broken` / `rough: <what>`; still colliding → mark `overlaps #N`; still carrying a Drop trait → mark `carries dropped: <trait>`.

**Done:** all items returned, every item passed or received its one rework pass, and the board file has every item's row with its final status.

## 4. Present

Open Storybook to the About page of the round's first item that passed (`<base>/?path=/story/<id>`) — `browser.open` plus `open <url>` for the user's browser. In chat, post one line per item: `#N Title — thesis`, the trait attribution for recombinations (`carries #3 timeline + #6 density`), and any board label (`broken`, `rough: …`, `overlaps #N`, `carries dropped: <trait>`). End by asking for reactions in any form. No item passed → report the round as blocked with each item's failure instead of presenting it.

From round 3 on, when the favourites of the last two rounds share most of their traits, add one line: `Converging on <X> — pick a winner, or another round?`

**Done:** Storybook is open on this round, every item has its line, and the reply ends asking for reactions.

## 5. Distill feedback

Read the user's free-form reaction. Record each item's verdict on the board; move each praised trait to Keep and each criticised trait to Drop, naming the item it came from. A trait named in both → ask which wins. User-steered changes ("more like X", "8 → 5 items") apply to the next round.

When the user names a winner for the round's focus and the Backlog still has open topics, **close the focus** instead of wrapping up:
1. Write `local://charcuterie-<concept>-winner-<focus>.md` with the same contents as the Wrap-up winner file.
2. Record it under a "Focus winners" heading on the board.
3. Promote the winner into the shared base, so its design becomes the Baseline for later rounds. Delegate if the change is large, then Look-check the Baseline.
4. Take the next Backlog topic, or the one the user names.

**Done:** every item the user mentioned has a verdict, and Keep/Drop reflect every trait they named. Then one of three things holds:
- the user named the final winner with an empty Backlog, or ended the board (→ Wrap-up);
- a focus closed and its winner was promoted (→ Plan the next focus);
- the next round is due (→ Plan).

## 6. Wrap-up

Only when the user names the final winner or ends the board:

1. Write `local://charcuterie-<concept>-winner.md`: the winning item (number, file, story id, thesis), the traits that made it win, notable runner-up traits worth porting, and a pointer to the board file.
2. Delete `<board root>/<concept>/` unless the user said to keep it; remove the board root if it is left empty.
3. `startedBySkill: yes` → stop Storybook (including the in-container process). Otherwise leave it running.

**Done:** the winner file exists, the board folder is gone or kept on request, and Storybook is stopped only if the skill started it.