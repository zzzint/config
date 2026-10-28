#!/usr/bin/env node
// Gives zstack a new version in the catalog and in its manifest.
//
//   node build/zstack/version.mjs
//
// omp upgrades a marketplace plugin only when the catalog lists a newer version, and records the installed
// version from the manifest, so both carry the same one. The UTC stamp is a numeric prerelease, which semver
// orders numerically, so every stamp sorts newer than the last within the same base version.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const CATALOG = join(ROOT, ".omp-plugin", "marketplace.json");
const MANIFEST = join(ROOT, "plugins", "zstack", ".claude-plugin", "plugin.json");

const catalog = JSON.parse(readFileSync(CATALOG, "utf8"));
const entry = catalog.plugins.find((plugin) => plugin.name === "zstack");
if (!entry) {
  console.error(".omp-plugin/marketplace.json has no zstack entry");
  process.exit(1);
}

// The manifest sits under the path that triggers the workflow, so a new base version is set there.
const manifest = JSON.parse(readFileSync(MANIFEST, "utf8"));
const base = manifest.version.split("-")[0];
const version = `${base}-${new Date().toISOString().replace(/\D/g, "").slice(0, 14)}`;

entry.version = version;
writeFileSync(CATALOG, `${JSON.stringify(catalog, null, 2)}\n`);
writeFileSync(MANIFEST, `${JSON.stringify({ ...manifest, version }, null, 2)}\n`);
console.log(version);
