---
name: pstack-omp
description: Maps the Cursor names in pstack skills to omp tools, agents, model roles, and paths. pstack skills tell you to read it once per session before you follow them.
disable-model-invocation: true
---

# pstack in omp

pstack skills use Cursor names. In omp, read this file once per session, then map each Cursor name in a skill with the tables below. `<pstack>` means the installed plugin folder that holds `skills/`, `agents/`, and `docs/`; `realpath skill://poteto-mode` in `bash` prints `<pstack>/skills/poteto-mode`. If a Cursor field has no row, drop it and say so. Never pass a field the omp tool schema does not list.

## Tools

| Cursor | omp |
| --- | --- |
| `Task` | The `task` tool. One call takes `{ context, tasks: [...] }`, one item per worker: `{ name, agent, task, solutionSpace }`. The Cursor prompt goes in `task`. Background every worker in the call shares goes in `context`. A Cursor `description` becomes `name`, CamelCase and at most 32 characters. `solutionSpace` is required: say whether the fix or design is given or which causes or designs are still open. Several Cursor `Task` calls in one turn become items of one call. For waves where one worker's result feeds the next, eval's `agent()` and `workpool()` take the same agents. |
| `AskQuestion` | The `ask` tool. Subagents and `omp -p` runs have no `ask`, so ask in plain text. |
| Open a todolist | The `todo` tool. `init` with the playbook's steps copied in verbatim as items, then mark each done as it finishes. |
| Run another pstack skill (`/name` or "the **name** skill") | `read skill://<name>` and follow it. Most pstack skills are hidden from the skill list, so a missing list entry does not mean the skill is absent. When you tell the user to type it, write `/skill:<name>`. |
| `Grep`, `Glob`, `Read` | `grep`, `glob`, `read`. |

## Subagent fields

| Cursor | omp |
| --- | --- |
| `subagent_type: generalPurpose` | Omit `agent`. The default `task` agent runs. |
| `poteto-agent` | `agent: "poteto-agent"` or `agent: "poteto-judge"`, chosen by the model row below. Both ship with this plugin and read `skill://poteto-mode` before any work, since subagents see the same skills as you. |
| `comment-sicko` | `agent: "comment-sicko"`. It ships with this plugin. |
| `readonly: true` | For a `generalPurpose` worker, `agent: "scout"`, whose tools are read-only. For a named agent, keep it, write "do not edit files" in `task`, and check `git status` afterward. `readonly: false` is the agent as named. |
| `environment: "cloud"` | `isolated: true` on the item. The field exists only when the `task.isolation.enabled` setting is on. Without it, run the worker in this checkout and say so in your reply. Name the branch or commit the worker starts from. |
| `environment: "local"` | Omit. |
| `cloud_base_branch: <b>` | Tell the isolated worker to check out `<b>` first. |
| `run_in_background: true` | Omit. Spawns run as background jobs and their results arrive on their own. Call `wait` only when you have nothing else to do. |
| `resume` | `write agent://<id>` with the follow-up. It revives a parked agent with its context intact. |
| `file_attachments` | List the paths in `task`. The worker reads them. |

## Models

The `task` tool has no `model` field. omp takes a worker's model from the `task.agentModelOverrides` setting for its agent, so pick the agent by the slug the skill names. An agent with no override runs on this session's model.

**Never run a worker on Grok.** pstack's defaults name Grok (`grok-*`, `cursor-grok-*`, `composer-*`) for code delegates, explorers, swarm workers and the second panel seat. In omp every one of those slugs means `poteto-agent`, and `poteto-agent` runs on `openai-codex/gpt-6.1-sol`. So a panel's default of Opus and Grok is Opus and GPT-6.1 sol, and a step that says Grok runs on GPT-6.1 sol. When a skill tells you to fall back to a Grok slug, use `poteto-agent` instead. Never pick, suggest or configure a Grok model, in an override or anywhere else.

| Cursor | omp |
| --- | --- |
| A `claude-<family>-<version>-<effort>` slug, such as `claude-opus-5-5-xhigh` | `agent: "poteto-judge"`. |
| A `grok-*`, `gpt-*`, or other non-Claude slug | `agent: "poteto-agent"`. |
| `inherit-parent` or `auto` | Omit `agent` when the step allows a `generalPurpose` worker. omp cannot pin a named agent to the parent's model, so a step that needs `poteto-agent` uses it as is. |
| A panel list, such as arena runners, architect runners, or interrogate reviewers | One worker per entry, each mapped by the rows above. When `poteto-agent` and `poteto-judge` run on the same model, the panel has one model, not several. Say so in the report. |
| The effort token in a slug | Set by the thinking suffix of the agent's override, such as `:xhigh`, not per call. Drop it from the call. |
| The `pstack-models.mdc` rule, `~/.cursor/rules/pstack-models.mdc` | `task.agentModelOverrides` in `~/.omp/agent/config.yml`, with one entry each for `poteto-agent` and `poteto-judge`. Each value is `<provider>/<model>:<thinking>`, such as `anthropic/claude-opus-5-5:xhigh`. |

## setup-pstack

Follow `setup-pstack` with these changes:

- Detect. `omp models` lists the models this install can use. Write a model as `<provider>/<model>:<thinking>`.
- Map. omp has two pstack seats. `poteto-agent` takes every role whose default is a Grok slug: feature, refactoring, bug-fix, perf-issue, hillclimb, how explorer, why investigators, reflect tooling, and swarm workers. `poteto-judge` takes every role whose default is a Claude slug: judgment and prose, hardest tasks, how explainer, why synthesizer, and reflect judgment. A panel runs one worker on each seat. `poteto-agent` runs on `openai-codex/gpt-6.1-sol` and `poteto-judge` on `anthropic/claude-opus-5-5`; offer only non-Grok models for either seat.
- Budget. The budget sets the thinking suffix of both seats: `max`, `xhigh`, `high`, or `medium`.
- Write. Show the two entries and ask before you change settings. Then set them under `task.agentModelOverrides` in `~/.omp/agent/config.yml`, or have the user pick them for each agent in the `/agents` hub. Write no `pstack-models.mdc`.

## Paths

| Cursor | omp |
| --- | --- |
| `.cursor/skills/`, `~/.cursor/skills/` | `.omp/skills/`, `~/.omp/agent/skills/`. |
| `~/.cursor/plugins/`, `.cursor-plugin/plugin.json` | `<pstack>`, from `realpath skill://poteto-mode`. Its manifest is `<pstack>/.claude-plugin/plugin.json`. |
| `.cursor/rules/*.mdc`, always-applied rules | A Markdown file with `alwaysApply: true` frontmatter in `.omp/rules/` for the project or `~/.omp/agent/rules/` for the user. Standing project instructions go in `AGENTS.md`. |
| A relative link in a pstack file | Resolve it against that file's folder. Inside a skill, read `skill://<skill>/<path>`. A link to `../<other>/SKILL.md` is `skill://<other>`. Anything that leaves `skills/`, such as `../../docs/guide/`, resolves under `<pstack>`. |
| `https://github.com/cursor/plugins/blob/main/pstack/<path>` | `<pstack>/<path>` when that file exists. Read the local copy and never fetch it. Give the user the URL when they need a link. |
| Transcripts in `~/.cursor/projects/<slug>/agent-transcripts/` | `~/.omp/agent/sessions/<slug>/`. Under your home folder, the slug is the workspace path with each `/` changed to `-`, so `~/Documents/proj` is `-Documents-proj`. Outside it, the slug is the full resolved path wrapped in `--`, so `/tmp/proj` on macOS is `--private-tmp-proj--`. The newest `.jsonl` directly in that folder is the current session. The folder with the same name holds its subagent transcripts. Eval's `archive` global searches past sessions with their recaps. Read only this workspace's sessions. |

## Cursor-only features

omp has no Cursor Automations, Bugbot, Cursor cloud agents, or built-in PR tool. When a step needs one, put one line in your reply, `Skipped in omp: <step>. <reason>.`, then go on to the next step. Do not stop, ask, or retry. When a later step needs what the skipped step made, such as a URL or a key, leave a placeholder and name it in the line.

| Cursor | omp |
| --- | --- |
| Cursor Automations: routines, `update_state` routine calls, `api2.cursor.sh/automations` webhooks, routine wakes, and `SendToUser` secret requests | Skip with the line. |
| Bugbot | Bugbot comments on a GitHub PR are ordinary review threads, so triage them with the forge command that the step gives. Skip a step that starts, waits for, or configures Bugbot when the PR has no Bugbot check or comment. |
| Cursor cloud agents | `environment: "cloud"` maps to `isolated: true`, as in Subagent fields. Skip a step that needs the cloud agent itself, such as its dashboard status or its own machine. |
| A built-in PR tool | Use the forge command that the step gives, such as `gh pr create`. That is not a skip, so write no line. |
