/**
 * Git for Job 1. Two rules, both non-negotiable:
 *
 *   1. `git commit -F <file>`, never `-m`. A PreToolUse hook substring-matches
 *      raw command text, so a generated message containing a dangerous-looking
 *      literal (a problem title, a code snippet) would block the commit. The
 *      message goes in a temp file OUTSIDE the repo and git reads it.
 *   2. No `Co-Authored-By: Claude` trailer, ever. These commits are Ayush's.
 *
 * Append-only: this module can stage, commit and push. It cannot reset, force
 * push or clean, and must never learn how.
 */

import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { REPO_ROOT } from "./manifest.js";

const GIT = "/usr/bin/git";

export interface GitResult {
  readonly status: number;
  readonly stdout: string;
  readonly stderr: string;
}

function git(args: readonly string[]): GitResult {
  const result = spawnSync(GIT, args as string[], {
    cwd: REPO_ROOT,
    encoding: "utf8",
  });
  return {
    status: result.status ?? 1,
    stdout: (result.stdout ?? "").trim(),
    stderr: (result.stderr ?? "").trim(),
  };
}

function gitOrThrow(args: readonly string[]): string {
  const result = git(args);
  if (result.status !== 0) {
    throw new Error(
      `git ${args.join(" ")} failed: ${result.stderr || result.stdout}`,
    );
  }
  return result.stdout;
}

/** Paths with staged or unstaged changes, relative to the repo root. */
export function changedPaths(): string[] {
  const output = gitOrThrow(["status", "--porcelain"]);
  if (!output) return [];
  return output
    .split("\n")
    .map((line) => line.slice(3).trim())
    .filter(Boolean);
}

export function stage(paths: readonly string[]): void {
  if (paths.length === 0) return;
  gitOrThrow(["add", "--", ...paths]);
}

export function hasStagedChanges(): boolean {
  return git(["diff", "--cached", "--quiet"]).status !== 0;
}

/**
 * Commit staged changes using a message file.
 *
 * `subject` must follow the conventional prefixes from ~/CLAUDE.md, and the
 * body should say why plus how it was verified.
 */
export function commit(subject: string, bodyLines: readonly string[]): boolean {
  if (!hasStagedChanges()) return false;

  // Outside the repo, so the message file can never be committed or scanned.
  const dir = mkdtempSync(join(tmpdir(), "lcp-commit-"));
  const messagePath = join(dir, "COMMIT_MSG.txt");
  const message = [subject, "", ...bodyLines].join("\n").replace(/\s+$/, "");

  try {
    writeFileSync(messagePath, `${message}\n`, "utf8");
    // -F, never -m. See the header comment.
    gitOrThrow(["commit", "-F", messagePath]);
    return true;
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

export function currentBranch(): string {
  return gitOrThrow(["rev-parse", "--abbrev-ref", "HEAD"]);
}

/** Plain fast-forward push. Never --force; that is on the global deny list. */
export function push(): void {
  const branch = currentBranch();
  gitOrThrow(["push", "origin", branch]);
}

export function headSummary(): string {
  const result = git(["log", "-1", "--pretty=%h %s"]);
  return result.status === 0 ? result.stdout : "(no commits yet)";
}

/** Fails loudly if a trailer ever sneaks in. Used by the verification pass. */
export function assertNoClaudeTrailer(range = "HEAD"): void {
  const result = git(["log", range, "--pretty=%B"]);
  if (result.status !== 0) return;
  if (/co-authored-by:.*claude/i.test(result.stdout)) {
    throw new Error(
      "a commit in this repo carries a Co-Authored-By: Claude trailer",
    );
  }
}
