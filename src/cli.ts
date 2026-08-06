#!/usr/bin/env node
/**
 * Job 1 — fetch. Runs in the GitHub Action daily, and locally on demand.
 *
 *   node dist/cli.js                  sync everything new since last time
 *   node dist/cli.js --dry-run        do the reads, write and commit nothing
 *   node dist/cli.js --only two-sum   re-pull one problem, new or not
 *   node dist/cli.js --no-push        commit locally, don't push
 *
 * Exit codes are load-bearing — the workflow branches on them:
 *   0  success (including "nothing new", which is the common case)
 *   2  the LeetCode session is dead -> the Action files an issue
 *   1  anything else
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

import {
  assertSignedIn,
  fetchNewAccepted,
  fetchQuestionMeta,
  fetchSubmissionDetail,
  findLatestAcceptedForSlug,
  SessionExpiredError,
  type Credentials,
  type QuestionMeta,
  type SubmissionSummary,
} from './leetcode.js';
import {
  DATA_DIR,
  QUESTIONS_DIR,
  RAW_DIR,
  readManifest,
  sha256,
  writeManifest,
  type Manifest,
  type ProblemEntry,
} from './manifest.js';
import { commit, hasStagedChanges, headSummary, push, stage } from './git.js';

const EXIT_OK = 0;
const EXIT_ERROR = 1;
const EXIT_SESSION_EXPIRED = 2;

interface Options {
  readonly dryRun: boolean;
  readonly only: string | null;
  readonly push: boolean;
}

function parseArgs(argv: readonly string[]): Options {
  let dryRun = false;
  let only: string | null = null;
  let shouldPush = true;

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]!;
    if (arg === '--dry-run') dryRun = true;
    else if (arg === '--no-push') shouldPush = false;
    else if (arg === '--only') {
      const next = argv[i + 1];
      if (!next) throw new Error('--only needs a problem slug');
      only = next;
      i += 1;
    } else if (arg.startsWith('--only=')) only = arg.slice('--only='.length);
    else throw new Error(`unknown argument: ${arg}`);
  }

  return { dryRun, only, push: shouldPush };
}

/**
 * Credentials come from the environment (GitHub Actions secrets) or, for local
 * runs, from a dotenv-style file. ~/.leetcode.env is preferred over a file
 * inside the repo: this repo is public, so a credential that physically cannot
 * be committed is better than one protected by .gitignore alone.
 */
function loadCredentials(): Credentials {
  const fromEnv = {
    session: process.env.LEETCODE_SESSION ?? '',
    csrfToken: process.env.LEETCODE_CSRF_TOKEN ?? '',
  };
  if (fromEnv.session && fromEnv.csrfToken) return fromEnv;

  const candidates = [join(homedir(), '.leetcode.env'), join(DATA_DIR, '..', '.env')];
  for (const path of candidates) {
    if (!existsSync(path)) continue;
    const parsed: Record<string, string> = {};
    for (const line of readFileSync(path, 'utf8').split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('=')) continue;
      const index = trimmed.indexOf('=');
      parsed[trimmed.slice(0, index).trim()] = trimmed.slice(index + 1).trim();
    }
    const session = parsed['LEETCODE_SESSION'] ?? '';
    const csrfToken = parsed['LEETCODE_CSRF_TOKEN'] ?? '';
    if (session && csrfToken) {
      console.log(`  credentials: ${path}`);
      return { session, csrfToken };
    }
  }

  throw new SessionExpiredError(
    'no credentials found — set LEETCODE_SESSION and LEETCODE_CSRF_TOKEN, or create ~/.leetcode.env (see docs/RUNBOOK.md)',
  );
}

function toEntry(
  meta: QuestionMeta,
  summary: SubmissionSummary,
  detail: {
    runtimeDisplay: string;
    runtimePercentile: number | null;
    memoryDisplay: string;
    memoryPercentile: number | null;
    langVerbose: string;
  },
  codeHash: string,
  previous: ProblemEntry | undefined,
): ProblemEntry {
  const unchanged = previous?.codeHash === codeHash;
  return {
    frontendId: meta.frontendId,
    title: meta.title,
    slug: meta.slug,
    difficulty: meta.difficulty,
    topics: meta.topics,
    url: `https://leetcode.com/problems/${meta.slug}/`,
    submissionId: summary.id,
    timestamp: Number(summary.timestamp),
    lang: detail.langVerbose,
    runtime: detail.runtimeDisplay,
    runtimePercentile: detail.runtimePercentile,
    memory: detail.memoryDisplay,
    memoryPercentile: detail.memoryPercentile,
    similar: meta.similar,
    codeHash,
    // Re-solving the same problem invalidates the annotation; identical code
    // keeps it, so Job 2 stays idempotent.
    annotationHash: unchanged ? (previous?.annotationHash ?? null) : null,
    annotated: unchanged ? (previous?.annotated ?? false) : false,
  };
}

function writeQuestionCache(meta: QuestionMeta): string {
  mkdirSync(QUESTIONS_DIR, { recursive: true });
  const path = join(QUESTIONS_DIR, `${meta.slug}.json`);
  // Note what is NOT here: `content` and `hints`. Both are LeetCode's own
  // words, this repo is public, and .githooks/pre-commit blocks them if they
  // ever come back. Job 2 restates the problem in Ayush's words instead.
  writeFileSync(path, `${JSON.stringify(meta, null, 2)}\n`, 'utf8');
  return path;
}

function writeRawCode(slug: string, code: string): string {
  mkdirSync(RAW_DIR, { recursive: true });
  const path = join(RAW_DIR, `${slug}.py`);
  // Verbatim, with a trailing newline only if the submission lacked one.
  writeFileSync(path, code.endsWith('\n') ? code : `${code}\n`, 'utf8');
  return path;
}

async function main(): Promise<number> {
  const options = parseArgs(process.argv.slice(2));
  console.log('Job 1 — LeetCode fetch');
  console.log(`  mode: ${options.dryRun ? 'DRY RUN (nothing is written)' : 'live'}`);
  console.log(`  head: ${headSummary()}`);

  const creds = loadCredentials();
  const username = await assertSignedIn(creds);
  console.log(`  signed in as: ${username}`);

  const manifest: Manifest = readManifest();
  console.log(`  known problems: ${Object.keys(manifest.problems).length}`);
  console.log(`  lastSyncedTimestamp: ${manifest.lastSyncedTimestamp}`);

  // --- discover -----------------------------------------------------------
  let targets: Map<string, SubmissionSummary>;
  if (options.only) {
    const found = await findLatestAcceptedForSlug(creds, options.only);
    if (!found) {
      console.error(`  no accepted submission found for slug "${options.only}"`);
      return EXIT_ERROR;
    }
    targets = new Map([[options.only, found]]);
    console.log(`  --only ${options.only}: submission ${found.id}`);
  } else {
    targets = await fetchNewAccepted(creds, manifest.lastSyncedTimestamp);
    console.log(`  new accepted problems: ${targets.size}`);
  }

  if (targets.size === 0) {
    console.log('\nnothing new since the last sync — no commit.');
    return EXIT_OK;
  }

  // --- hydrate ------------------------------------------------------------
  const touched: string[] = [];
  let newest = manifest.lastSyncedTimestamp;
  const summaries: string[] = [];

  for (const [slug, summary] of targets) {
    console.log(`\n  ${slug} (submission ${summary.id})`);
    const detail = await fetchSubmissionDetail(creds, summary.id);
    const meta = await fetchQuestionMeta(creds, slug);
    const codeHash = sha256(detail.code);
    const previous = manifest.problems[slug];

    console.log(`    ${meta.frontendId}. ${meta.title} [${meta.difficulty}]`);
    console.log(`    ${detail.code.split('\n').length} lines, sha256 ${codeHash.slice(0, 12)}`);
    if (previous && previous.codeHash === codeHash) {
      console.log('    code identical to what is already stored — annotation kept');
    }

    newest = Math.max(newest, Number(summary.timestamp));

    if (options.dryRun) {
      console.log('    DRY RUN: not writing');
      continue;
    }

    touched.push(writeRawCode(slug, detail.code));
    touched.push(writeQuestionCache(meta));
    manifest.problems[slug] = toEntry(meta, summary, detail, codeHash, previous);
    summaries.push(`${meta.frontendId}. ${meta.title} (${meta.difficulty})`);
  }

  if (options.dryRun) {
    console.log('\nDRY RUN complete — no files written, no commit, manifest untouched.');
    return EXIT_OK;
  }

  // --- commit -------------------------------------------------------------
  manifest.lastSyncedTimestamp = newest;
  manifest.lastSyncedAt = new Date().toISOString();
  writeManifest(manifest);
  touched.push(join(DATA_DIR, 'manifest.json'));

  stage(touched);
  if (!hasStagedChanges()) {
    console.log('\nfetched data was byte-identical to what is committed — no commit.');
    return EXIT_OK;
  }

  const count = summaries.length;
  const subject = `chore: sync ${count} new submission${count === 1 ? '' : 's'}`;
  const committed = commit(subject, [
    'Pulled by Job 1 (GitHub Action) from the authenticated LeetCode GraphQL API.',
    '',
    ...summaries.map((line) => `- ${line}`),
    '',
    'Verified: authenticated userStatus check passed before fetching, and every',
    'submission returned non-empty code. data/raw/*.py is the verbatim',
    'submission and is the reference copy the AST gate compares against.',
    'Question metadata excludes `content` and `hints` — this repo is public and',
    'those are LeetCode\'s copyrighted prose.',
  ]);

  if (!committed) {
    console.log('\nnothing staged — no commit.');
    return EXIT_OK;
  }
  console.log(`\ncommitted: ${headSummary()}`);

  if (options.push) {
    push();
    console.log('pushed to origin.');
  } else {
    console.log('--no-push: left the commit local.');
  }

  return EXIT_OK;
}

main()
  .then((code) => process.exit(code))
  .catch((error: unknown) => {
    if (error instanceof SessionExpiredError) {
      console.error('\n=== LEETCODE SESSION EXPIRED ===');
      console.error(error.message);
      console.error('This is NOT "no new solves". See docs/RUNBOOK.md to refresh the cookie.');
      process.exit(EXIT_SESSION_EXPIRED);
    }
    console.error('\nJob 1 failed:', error instanceof Error ? error.stack : String(error));
    process.exit(EXIT_ERROR);
  });
