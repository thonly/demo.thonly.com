#!/usr/bin/env node
// The drift guard for the vendored brand layer.
//
// WHY A DETECTOR AND NOT A PACKAGE — the same argument check-shared.mjs makes,
// and it survives this case unchanged. seysays, playsey, sayyourname and
// 333.eco each have their own CI and their own deploy cadence; no module can
// span them, so a detector does. A57 originally proposed a tag-pinned git
// dependency; that was reconsidered here because a version RANGE is drift with
// a number on it, and because of the line below.
//
// NO NETWORK, NO CREDENTIALS, NO SIBLING CHECKOUT in --check mode. That is the
// reason this works where fetching a package would not: CI is
// actions/checkout@v4 + `npm ci` with no .npmrc anywhere in the estate, so the
// guard needs nothing it does not already have and cannot be disabled by a
// missing token.
//
// ⚠️ INTEGRITY IS NOT CURRENCY, and conflating them is how four repos sat three
// minor versions behind while every guard reported green. --check answers "do
// my files match MY lock" — it is local, offline, and it cannot answer "is my
// lock the current one", because a repo that has fallen behind is internally
// consistent. That was left to "an older version string shows up in a pull
// request", which is a person remembering, and on 2026-09-01 the person had not:
// package v1.3.0, all four consumers v1.0.0.
//
// So currency is a SECOND MODE with different rules, and the rules differ
// because the questions do. --currency --against <checkout> compares this
// repo's lock version to the package's. It needs the package, so it needs
// either a sibling checkout or a network fetch — which is exactly why it must
// not run in the build. It runs on a SCHEDULE, where being unable to reach
// GitHub means a red scheduled job and not a blocked deploy.
//
// brand.333.eco is a PUBLIC repository, so the scheduled workflow checks it out
// with no token, and the "cannot be disabled by a missing credential" property
// survives into the second mode intact.
//
// THREE FILES, AND ONLY ONE OF THEM DIFFERS PER REPO:
//   brand.lock       every package file -> sha256, plus a version.
//                    BYTE-IDENTICAL in every consumer. A repo that falls
//                    behind carries an older version string, which shows up as
//                    a diff in a pull request rather than as a mystery.
//   brand.uses       which files THIS repo vendors, and where they live.
//                    The one file that must differ — the same role config.ts
//                    plays in the check-shared set.
//   check-brand.mjs  this file. Byte-identical everywhere.
//
// House rules followed: node built-ins only, assertions that name the fix and
// not just the failure, and a non-zero exit that a workflow notices.

import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, copyFileSync, existsSync, readdirSync } from "node:fs";
import { dirname, resolve, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const BASE = resolve(HERE, "..");

const LOCK = join(BASE, "brand.lock");
const USES = join(BASE, "brand.uses");

const sha = (path) => createHash("sha256").update(readFileSync(path)).digest("hex");

const die = (msg) => {
    console.error(`check-brand: ${msg}`);
    process.exit(1);
};

const args = process.argv.slice(2);
const argOf = (flag) => {
    const i = args.indexOf(flag);
    return i === -1 ? null : args[i + 1];
};

/* ------------------------------------------------------- the package itself ---
   Run inside brand.333.eco, this rewrites or verifies brand.lock against the
   real files. Detected by the presence of the package's own directories rather
   than by a flag, so it cannot be run in the wrong mode by accident. */

const isPackageRepo = existsSync(join(BASE, "css")) && existsSync(join(BASE, "data"));

const packageFiles = () => {
    const out = [];
    // ⭐ v1.4.0 — `qr/` joined (the B-QR recipe, A295). A new directory goes in this list AND in package.json `files`
    //   (check-publish.mjs fails until it is shipped), and a consumer finds it through the lock, never through a rule here.
    for (const dir of ["css", "emblem", "qr"]) {
        for (const f of readdirSync(join(BASE, dir)).sort()) out.push(`${dir}/${f}`);
    }
    return out;
};

if (isPackageRepo) {
    const version = JSON.parse(readFileSync(join(BASE, "data", "brand.json"), "utf8")).version;
    const files = Object.fromEntries(packageFiles().map((f) => [f, sha(join(BASE, f))]));
    const body = JSON.stringify({ version, files }, null, 4) + "\n";

    if (args.includes("--write")) {
        writeFileSync(LOCK, body);
        console.log(`check-brand: wrote brand.lock (v${version}, ${Object.keys(files).length} files)`);
        process.exit(0);
    }
    if (!existsSync(LOCK)) die("brand.lock is missing. Run: node scripts/check-brand.mjs --write");
    if (readFileSync(LOCK, "utf8") !== body) {
        die(
            "brand.lock does not match the files in css/, emblem/ and qr/.\n" +
                "  Run: node scripts/check-brand.mjs --write\n" +
                "  Then commit brand.lock in the SAME commit as the file it locks, or a\n" +
                "  consumer will sync bytes the lock does not describe."
        );
    }
    console.log(`check-brand: brand.lock is current (v${version})`);
    process.exit(0);
}

/* ------------------------------------------------------------- a consumer --- */

if (!existsSync(USES)) {
    die(
        "brand.uses is missing.\n" +
            "  It declares which brand files this repo vendors and where they live:\n" +
            '    { "dir": "partials", "files": ["tokens.css", "theme-3block.css", ...] }\n' +
            "  It is the one file in this set that differs per repo."
    );
}

const uses = JSON.parse(readFileSync(USES, "utf8"));
const targetDir = resolve(BASE, uses.dir);

const from = argOf("--from");
if (from) {
    // Sync from a sibling checkout. A deliberate, reviewable act — never
    // something CI does, which is why it is not the default and not --check.
    const src = resolve(from);
    if (!existsSync(join(src, "brand.lock"))) {
        die(`${src} has no brand.lock — is --from pointing at the brand.333.eco checkout?`);
    }
    const theirs = JSON.parse(readFileSync(join(src, "brand.lock"), "utf8")).files;
    for (const name of uses.files) {
        const origin = join(src, dirOf(name, theirs), name);
        if (!existsSync(origin)) die(`${origin} is missing from the brand checkout`);
        copyFileSync(origin, join(targetDir, name));
    }
    copyFileSync(join(src, "brand.lock"), LOCK);
    copyFileSync(join(src, "scripts", "check-brand.mjs"), join(HERE, "check-brand.mjs"));
    const v = JSON.parse(readFileSync(LOCK, "utf8")).version;
    console.log(
        `check-brand: synced ${uses.files.length} files + brand.lock from ${src} (v${v})`
    );
    process.exit(0);
}

/* Which package directory a vendored file lives in — read from the LOCK, whose keys are `dir/name`, so a new directory
   (qr/, v1.4.0) needs no rule here. ⛔ Two package files with one name in two directories would be ambiguous, and the
   lock is refused rather than guessed. Older locks (≤ v1.3.0, css/ and emblem/ only) resolve the same way. */
function dirOf(name, files) {
    const hits = Object.keys(files).filter((k) => k.slice(k.indexOf("/") + 1) === name);
    if (hits.length > 1) die(`brand.lock names ${name} in two directories (${hits.join(", ")}) — rename one upstream.`);
    return hits.length ? hits[0].slice(0, hits[0].indexOf("/")) : name.endsWith(".css") ? "css" : "emblem";
}

if (!existsSync(LOCK)) {
    die("brand.lock is missing. Sync it: npm run brand:sync -- --from <path to brand.333.eco>");
}

const lock = JSON.parse(readFileSync(LOCK, "utf8"));

/* ---------------------------------------------------------------- currency ---
   "Is my lock the current one?" — the question --check structurally cannot ask.
   Compared as VERSION STRINGS and not as hashes, deliberately: a consumer
   vendors a subset (brand.uses), so its files can legitimately differ from the
   package's full set while being perfectly current. The version is the only
   thing every consumer holds in common with the package, which is why the lock
   carries one at all. */

if (args.includes("--currency")) {
    const against = argOf("--against");
    if (!against) {
        die(
            "--currency needs --against <path to a brand.333.eco checkout>.\n" +
                "  In CI, check the public package out beside this repo:\n" +
                "    - uses: actions/checkout@v4\n" +
                "      with: { repository: 333eco/brand.333.eco, path: .brand }"
        );
    }
    const theirLock = resolve(against, "brand.lock");
    if (!existsSync(theirLock)) {
        die(`${theirLock} does not exist — is --against pointing at the brand.333.eco checkout?`);
    }
    const theirs = JSON.parse(readFileSync(theirLock, "utf8")).version;
    const mine = lock.version;

    if (mine === theirs) {
        console.log(`check-brand: current (v${mine})`);
        process.exit(0);
    }

    /* Numeric compare, so "1.10.0" is not judged older than "1.9.0" the way a
       string compare would have it. A consumer AHEAD of the package is not a
       lag — it means someone edited the brand layer here, which --check already
       catches by hash and reports with the right fix. Say so rather than
       telling them to sync backwards. */
    const parts = (v) => v.split(".").map(Number);
    const [a, b] = [parts(mine), parts(theirs)];
    const ahead = a.some((n, i) => n !== b[i] && n > b[i] && a.slice(0, i).every((m, j) => m === b[j]));

    if (ahead) {
        die(
            `this repo's brand.lock (v${mine}) is AHEAD of the package (v${theirs}).\n` +
                "  That is not a stale consumer — the brand layer was edited here, or the\n" +
                "  package was rolled back. Edits belong upstream in brand.333.eco."
        );
    }

    die(
        `brand layer is BEHIND: this repo is on v${mine}, the package is on v${theirs}.\n` +
            "  Take the current layer, review the diff, and commit it:\n" +
            "    npm run brand:sync -- --from <path to brand.333.eco>\n" +
            "  This is a scheduled check, not a build gate — nothing is blocked by it."
    );
}

const problems = [];

for (const name of uses.files) {
    const key = `${dirOf(name, lock.files)}/${name}`;
    const expected = lock.files[key];
    const local = join(targetDir, name);

    if (!expected) {
        problems.push(`${name} is listed in brand.uses but not in brand.lock (v${lock.version}) — is the name right?`);
        continue;
    }
    if (!existsSync(local)) {
        problems.push(`${name} is listed in brand.uses but missing from ${uses.dir}/`);
        continue;
    }
    const actual = sha(local);
    if (actual !== expected) {
        problems.push(
            `${uses.dir}/${name} does not match brand.lock v${lock.version}.\n` +
                `      expected ${expected.slice(0, 16)}…\n` +
                `      actual   ${actual.slice(0, 16)}…\n` +
                `      A brand file was edited HERE. Edits belong upstream in brand.333.eco;\n` +
                `      make the change there, bump the lock, and re-sync every consumer.`
        );
    }
}

if (problems.length) {
    console.error("check-brand: FAILED\n");
    for (const p of problems) console.error(`  - ${p}`);
    console.error(
        `\n  To take the current brand layer:\n` +
            `    npm run brand:sync -- --from ../../333.eco/brand.333.eco\n`
    );
    process.exit(1);
}

console.log(
    `check-brand: ${uses.files.length} files match brand.lock v${lock.version}`
);
