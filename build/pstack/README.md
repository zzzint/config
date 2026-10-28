# pstack for omp

[pstack](https://github.com/cursor/plugins/tree/main/pstack) is poteto's skill set for Cursor. This folder builds an omp copy of it into `plugins/pstack` and publishes it through this repository's omp marketplace catalog, `.omp-plugin/marketplace.json`.

- `plugins/pstack/` is generated. Do not edit it by hand.
- `omp/adapter.md` becomes the `pstack-omp` skill, which maps the Cursor names in pstack skills to omp tools, agents, model settings, and paths. Every pstack skill that uses a Cursor name gets a line telling the model to read it.
- `omp/agents/` holds the omp versions of `poteto-agent` and `poteto-judge`. They replace upstream's `poteto-agent`, which looks for pstack under `~/.cursor/plugins`.
- `generate.mjs` builds `plugins/pstack/` from a checkout of `cursor/plugins`.

## Install

```sh
omp plugin marketplace add zzzint/config
omp plugin install pstack@zzzint
```

Then run `/skill:poteto-mode` at the start of a task. `/skill:setup-pstack` picks the models `poteto-agent` and `poteto-judge` run on, through `task.agentModelOverrides` in `~/.omp/agent/config.yml`. Without an override, both run on the session's model.

## Updates

The `pstack` workflow runs daily. It rebuilds `plugins/pstack/` from `cursor/plugins` main and commits straight to `main` when anything changed, with a new catalog version. Pick it up with:

```sh
omp plugin marketplace update zzzint
omp plugin upgrade pstack@zzzint
```

The build fails when upstream starts using a Cursor name that `omp/adapter.md` has no row for. It reads that list from upstream's own Claude Code generator, `scripts/generate-pstack-harness-trees.mjs`. A failed run means the adapter needs a row; add it and push.

## Rebuild locally

```sh
git clone --depth 1 --filter=blob:none --sparse https://github.com/cursor/plugins /tmp/cursor-plugins
git -C /tmp/cursor-plugins sparse-checkout set pstack scripts
node build/pstack/generate.mjs /tmp/cursor-plugins          # write plugins/pstack/ when it changed
node build/pstack/generate.mjs /tmp/cursor-plugins --check  # fail when plugins/pstack/ is out of date
```

## Why the tree ships a Claude-format manifest

The tree has only `.claude-plugin/plugin.json`, with no root `plugin.json`. A root manifest that declares the Agent Plugins schema sends skills to omp's strict loader, which drops every skill marked `disable-model-invocation`, and that is all but one of pstack's. The Claude loader keeps those skills out of the skill list but readable through `skill://` and `/skill:`.

The same loader ignores an agent's `model` frontmatter, so models are set with `task.agentModelOverrides` rather than in the agent files.
