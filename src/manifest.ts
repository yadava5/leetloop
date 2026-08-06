/**
 * data/manifest.json — the single piece of state shared by the two jobs.
 *
 * Job 1 writes everything except `annotated` / `annotationHash`, which it only
 * ever resets to "needs work". Job 2 writes only those two fields. Nothing else
 * in the repo carries state, so there is nothing to get out of sync.
 */

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

export const REPO_ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
export const DATA_DIR = join(REPO_ROOT, 'data');
export const RAW_DIR = join(DATA_DIR, 'raw');
export const QUESTIONS_DIR = join(DATA_DIR, 'questions');
export const PROBLEMS_DIR = join(REPO_ROOT, 'problems');
export const INDEXES_DIR = join(REPO_ROOT, 'indexes');
export const MANIFEST_PATH = join(DATA_DIR, 'manifest.json');

export const MANIFEST_VERSION = 1;

export interface TopicTag {
  readonly name: string;
  readonly slug: string;
}

export interface ProblemEntry {
  /** LeetCode's displayed problem number, e.g. "1" for Two Sum. */
  frontendId: string;
  title: string;
  slug: string;
  difficulty: string;
  topics: readonly string[];
  url: string;
  /** Submission that produced data/raw/<slug>.py. */
  submissionId: string;
  /** Unix seconds, when it was accepted. Drives indexes/review-queue.md. */
  timestamp: number;
  lang: string;
  runtime: string;
  runtimePercentile: number | null;
  memory: string;
  memoryPercentile: number | null;
  /** Slugs of LeetCode's "similar questions", for cross-linking. */
  similar: readonly string[];
  /** sha256 of the raw submitted code. */
  codeHash: string;
  /** codeHash that the current annotation was written against. */
  annotationHash: string | null;
  annotated: boolean;
}

export interface Manifest {
  version: number;
  /** Highest submission timestamp Job 1 has already ingested. */
  lastSyncedTimestamp: number;
  lastSyncedAt: string | null;
  problems: Record<string, ProblemEntry>;
}

export function emptyManifest(): Manifest {
  return {
    version: MANIFEST_VERSION,
    lastSyncedTimestamp: 0,
    lastSyncedAt: null,
    problems: {},
  };
}

export function readManifest(): Manifest {
  if (!existsSync(MANIFEST_PATH)) return emptyManifest();
  const parsed = JSON.parse(readFileSync(MANIFEST_PATH, 'utf8')) as Manifest;
  if (parsed.version !== MANIFEST_VERSION) {
    throw new Error(
      `manifest version ${parsed.version} but this build expects ${MANIFEST_VERSION}`,
    );
  }
  return parsed;
}

export function writeManifest(manifest: Manifest): void {
  mkdirSync(DATA_DIR, { recursive: true });
  const ordered: Record<string, ProblemEntry> = {};
  for (const slug of Object.keys(manifest.problems).sort()) {
    ordered[slug] = manifest.problems[slug]!;
  }
  const out: Manifest = { ...manifest, problems: ordered };
  writeFileSync(MANIFEST_PATH, `${JSON.stringify(out, null, 2)}\n`, 'utf8');
}

export function sha256(text: string): string {
  return createHash('sha256').update(text, 'utf8').digest('hex');
}

/** problems/0001-two-sum — zero-padded so the directory sorts like LeetCode. */
export function problemFolder(frontendId: string, slug: string): string {
  const padded = /^\d+$/.test(frontendId) ? frontendId.padStart(4, '0') : frontendId;
  return `${padded}-${slug}`;
}

/** Entries Job 2 still owes work on. */
export function pendingAnnotation(manifest: Manifest): ProblemEntry[] {
  return Object.values(manifest.problems).filter(
    (entry) => !entry.annotated || entry.annotationHash !== entry.codeHash,
  );
}
