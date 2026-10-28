#!/usr/bin/env node
// Builds plugins/pstack, the omp copy of pstack, from a checkout of cursor/plugins.
//
//   node build/pstack/generate.mjs <cursor-plugins checkout>          write the tree when it changed
//   node build/pstack/generate.mjs <cursor-plugins checkout> --check  fail when the tree is out of date

import { chmodSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, posix, relative, resolve as resolvePath } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..", "..");
const OUT = join(ROOT, "plugins", "pstack");
const OMP = join(HERE, "omp");
const CATALOG = join(ROOT, ".omp-plugin", "marketplace.json");
const PLUGIN = "pstack";
const ADAPTER_SKILL = "pstack-omp";
const GUIDE = "docs/guide";
const GITHUB = "https://github.com/cursor/plugins";
const LINK = /\]\(([^)\s]+)\)/g;
const SKILL_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const ADAPTER_LINE =
  `In omp, read \`skill://${ADAPTER_SKILL}\` once per session before you follow this skill. ` +
  "It maps the Cursor names in pstack skills to omp.";

const [upstreamArg] = process.argv.slice(2).filter((arg) => !arg.startsWith("--"));
if (!upstreamArg) fail("usage: node build/pstack/generate.mjs <cursor-plugins checkout> [--check]");
const UPSTREAM = resolvePath(upstreamArg);
const PSTACK = join(UPSTREAM, "pstack");
const SKILLS = join(PSTACK, "skills");

function fail(message) {
  console.log(`FAIL ${message}`);
  process.exit(1);
}

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    if (name === ".DS_Store" || name === "node_modules") return [];
    const path = join(dir, name);
    return statSync(path).isDirectory() ? walk(path) : [path];
  });
}

function file(path) {
  return { bytes: readFileSync(path), executable: (statSync(path).mode & 0o111) !== 0 };
}

// Upstream's Claude Code generator owns the list of Cursor names that need a harness mapping. Reading it from
// there means a name upstream adds fails this build until the omp adapter maps it.
function upstreamTerms() {
  const source = readFileSync(join(UPSTREAM, "scripts", "generate-pstack-harness-trees.mjs"), "utf8");
  const terms = source.match(/^const TERMS = (\[[\s\S]*?^\]);$/m)?.[1];
  const routeKey = source.match(/^const ROUTE_KEY = (".*");$/m)?.[1];
  if (!terms || !routeKey) fail("upstream generator no longer declares TERMS and ROUTE_KEY where this script reads them");
  return { terms: new Function(`return ${terms}`)(), routeKey: JSON.parse(routeKey) };
}

const { terms, routeKey } = upstreamTerms();
const skills = readdirSync(SKILLS).filter((name) => existsSync(join(SKILLS, name, "SKILL.md")));
if (skills.includes(ADAPTER_SKILL)) fail(`upstream now ships a skill named ${ADAPTER_SKILL}; rename the omp adapter`);
const ompAgents = readdirSync(join(OMP, "agents")).filter((name) => name.endsWith(".md"));
const upstreamAgents = readdirSync(join(PSTACK, "agents")).filter((name) => name.endsWith(".md"));

function cursorNames(paths, others) {
  const route = new RegExp(`the \\*\\*(?<bold>${others})\\*\\* skill|\`/(?<command>${others})\``, "g");
  const namesBareSkill = (line) =>
    [...line.matchAll(route)].some(({ groups }) => !line.includes(`(../${groups.bold ?? groups.command}/`));
  const found = new Set();
  for (const path of paths) {
    const text = readFileSync(path, "utf8");
    for (const term of terms) if (term.re.test(text)) found.add(term.key);
    if (text.split("\n").some(namesBareSkill)) found.add(routeKey);
  }
  return found;
}

const problems = [];
const users = new Map();
const wrapped = new Set();
const allSkills = skills.join("|");
for (const skill of skills) {
  const dir = join(SKILLS, skill);
  const others = skills.filter((name) => name !== skill).join("|");
  const found = cursorNames(walk(dir).filter((path) => path.endsWith(".md")), others);
  const text = readFileSync(join(dir, "SKILL.md"), "utf8");
  if (found.size > 0) {
    if (/^# /m.test(text)) wrapped.add(skill);
    else problems.push(`skills/${skill}/SKILL.md uses Cursor names but has no H1 to put the adapter line under`);
  }
  for (const key of found) users.set(key, [...(users.get(key) ?? []), `skills/${skill}`]);
  // omp resolves `skill://<name>` by frontmatter name while pstack links skills by folder, so the two must match.
  const frontmatter = text.match(/^---\n([\s\S]*?)\n---/)?.[1] ?? "";
  const name = frontmatter.match(/^name:(.*)$/m)?.[1].trim().replace(/^(["'])(.*)\1$/, "$2");
  if (name !== skill) problems.push(`skills/${skill}/SKILL.md has name ${JSON.stringify(name ?? "")}, not its folder name ${skill}`);
  if (!SKILL_NAME.test(skill) || skill.length > 64) problems.push(`skills/${skill} is not lowercase words joined by hyphens, at most 64 characters`);
}
// Upstream agents that the omp folder does not replace ship as they are, so they get the same check.
for (const agent of upstreamAgents.filter((name) => !ompAgents.includes(name))) {
  for (const key of cursorNames([join(PSTACK, "agents", agent)], allSkills)) {
    users.set(key, [...(users.get(key) ?? []), `agents/${agent}`]);
  }
}
const adapter = readFileSync(join(OMP, "adapter.md"), "utf8");
for (const [key, using] of users) {
  if (!adapter.includes(key)) problems.push(`omp adapter has no row for ${key}, used by ${using.join(", ")}`);
}
for (const problem of problems) console.log(`FAIL ${problem}`);
if (problems.length > 0) process.exit(1);

// The pstack-relative path that a relative link in `from` points at, if that path exists upstream.
function resolveLink(from, href) {
  const target = href.replace(/[#?].*/, "");
  if (!target || /^[a-z][a-z0-9+.-]*:/i.test(target)) return undefined;
  const path = posix.join(posix.dirname(from), target).replace(/\/$/, "");
  return existsSync(join(PSTACK, path)) ? path : undefined;
}

function has(files, path) {
  return files.has(path) || [...files.keys()].some((key) => key.startsWith(`${path}/`));
}

function render() {
  const copies = [...walk(SKILLS), ...walk(join(PSTACK, GUIDE)), join(PSTACK, "README.md"), join(PSTACK, "LICENSE")];
  const files = new Map(copies.map((path) => [relative(PSTACK, path), file(path)]));
  for (const agent of upstreamAgents) files.set(`agents/${agent}`, file(join(PSTACK, "agents", agent)));
  for (const agent of ompAgents) files.set(`agents/${agent}`, file(join(OMP, "agents", agent)));
  files.set(`skills/${ADAPTER_SKILL}/SKILL.md`, file(join(OMP, "adapter.md")));
  for (const skill of wrapped) {
    const entry = files.get(`skills/${skill}/SKILL.md`);
    entry.bytes = Buffer.from(entry.bytes.toString("utf8").replace(/^(# .*)\n+/m, `$1\n\n${ADAPTER_LINE}\n\n`));
  }
  // A relative link to an upstream pstack file the tree leaves out, such as pstack/assets, points at GitHub instead.
  for (const [path, entry] of files) {
    if (!path.endsWith(".md")) continue;
    const text = entry.bytes.toString("utf8").replace(LINK, (link, href) => {
      const target = resolveLink(path, href);
      if (!target || target.split("/")[0] === ".." || has(files, target)) return link;
      const kind = statSync(join(PSTACK, target)).isDirectory() ? "tree" : "blob";
      return `](${GITHUB}/${kind}/main/pstack/${target}${href.slice(href.search(/[#?]|$/))})`;
    });
    entry.bytes = Buffer.from(text);
  }
  return files;
}

const files = render();
const dangling = [];
for (const [path, entry] of files) {
  if (!path.endsWith(".md")) continue;
  for (const [, href] of entry.bytes.toString("utf8").matchAll(LINK)) {
    const target = resolveLink(path, href);
    if (target && !has(files, target)) dangling.push(`plugins/pstack/${path} links to ${href}, which is not in the tree`);
  }
}
for (const link of dangling) console.log(`FAIL ${link}`);
if (dangling.length > 0) process.exit(1);

// The tree ships only a Claude-format manifest. A root plugin.json declaring the Agent Plugins schema routes skills
// to omp's strict loader, which drops every skill with `disable-model-invocation`, and that is all but one of them.
// The Claude loader keeps them hidden from the skill list and readable through skill://.
//
// omp records a plugin's version from its manifest and reinstalls it only when the catalog lists a newer one,
// so the manifest and the catalog carry the same version and every content change gets a new one.
// The upstream version leads so an upstream release always sorts newer; the UTC stamp orders rebuilds within it.
const MANIFEST = ".claude-plugin/plugin.json";
const { $schema: _agentPluginsSchema, ...upstreamManifest } = JSON.parse(readFileSync(join(PSTACK, "plugin.json"), "utf8"));
const upstreamVersion = upstreamManifest.version;
const catalog = JSON.parse(readFileSync(CATALOG, "utf8"));
const entry = catalog.plugins.find((plugin) => plugin.name === PLUGIN);
if (!entry) fail(`${relative(ROOT, CATALOG)} has no ${PLUGIN} entry`);

function stampManifest(version) {
  files.set(MANIFEST, { bytes: Buffer.from(`${JSON.stringify({ ...upstreamManifest, version }, null, 2)}\n`), executable: false });
}

stampManifest(entry.version);
const onDisk = new Map(existsSync(OUT) ? walk(OUT).map((path) => [relative(OUT, path), file(path)]) : []);
const drifted = [...new Set([...files.keys(), ...onDisk.keys()])].sort().filter((path) => {
  const [want, have] = [files.get(path), onDisk.get(path)];
  return !want || !have || !want.bytes.equals(have.bytes) || want.executable !== have.executable;
});
if (!entry.version.startsWith(`${upstreamVersion}-omp.`) && !drifted.includes(MANIFEST)) drifted.push(MANIFEST);

if (drifted.length === 0) {
  console.log("plugins/pstack is up to date.");
  process.exit(0);
}
if (process.argv.includes("--check")) {
  for (const path of drifted.slice(0, 20)) console.log(`plugins/pstack/${path}`);
  fail("plugins/pstack is out of date. Run `node build/pstack/generate.mjs <cursor-plugins checkout>` and commit the result.");
}

entry.version = `${upstreamVersion}-omp.${new Date().toISOString().replace(/\D/g, "").slice(0, 14)}`;
stampManifest(entry.version);
rmSync(OUT, { recursive: true, force: true });
for (const [path, { bytes, executable }] of files) {
  mkdirSync(dirname(join(OUT, path)), { recursive: true });
  writeFileSync(join(OUT, path), bytes);
  chmodSync(join(OUT, path), executable ? 0o755 : 0o644);
}
writeFileSync(CATALOG, `${JSON.stringify(catalog, null, 2)}\n`);

console.log(`${skills.length + 1} skills, ${wrapped.size} SKILL.md files with the adapter line, ${drifted.length} files changed, version ${entry.version}`);
