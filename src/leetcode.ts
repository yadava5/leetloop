/**
 * LeetCode access for Job 1.
 *
 * Deliberately zero runtime dependencies: native `fetch` against
 * leetcode.com/graphql. The three query shapes below were verified against the
 * live authenticated API before this file was written, so a wrapper library
 * would add a dependency and a moving part without adding certainty. This runs
 * unattended in a GitHub Action; fewer things to break is the feature.
 *
 * There is NO model call and NO Anthropic API key here. This half of the system
 * holds the LeetCode cookie and nothing else.
 */

const ENDPOINT = "https://leetcode.com/graphql";

/** Community-standard safe cadence. LeetCode publishes no numeric limit. */
const MIN_REQUEST_INTERVAL_MS = 1000;
const MAX_RETRIES = 5;

/**
 * The cookie is dead or was rejected. Must never be confused with "no new
 * solves" — that mistake would silently stop the pipeline for weeks.
 */
export class SessionExpiredError extends Error {
  constructor(detail: string) {
    super(`LeetCode session rejected: ${detail}`);
    this.name = "SessionExpiredError";
  }
}

export interface Credentials {
  readonly session: string;
  readonly csrfToken: string;
}

export interface SubmissionSummary {
  readonly id: string;
  readonly title: string;
  readonly titleSlug: string;
  readonly statusDisplay: string;
  readonly lang: string;
  readonly timestamp: string;
}

export interface SubmissionDetail {
  readonly code: string;
  readonly timestamp: number;
  readonly runtimeDisplay: string;
  readonly runtimePercentile: number | null;
  readonly memoryDisplay: string;
  readonly memoryPercentile: number | null;
  readonly langVerbose: string;
}

/**
 * Question metadata AFTER stripping LeetCode's own prose.
 *
 * `content` (the problem statement) and `hints` are fetched — they are needed
 * to decide nothing, so they are simply never returned. This repo is public and
 * those fields are copyrighted. The pre-commit hook enforces the same rule
 * mechanically in case this ever regresses.
 */
export interface QuestionMeta {
  readonly questionId: string;
  readonly frontendId: string;
  readonly title: string;
  readonly slug: string;
  readonly difficulty: string;
  readonly topics: readonly string[];
  readonly similar: readonly string[];
}

let lastRequestAt = 0;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function throttle(): Promise<void> {
  const waited = Date.now() - lastRequestAt;
  if (waited < MIN_REQUEST_INTERVAL_MS) {
    await sleep(MIN_REQUEST_INTERVAL_MS - waited);
  }
  lastRequestAt = Date.now();
}

function looksLikeAuthFailure(text: string): boolean {
  const lowered = text.toLowerCase();
  return (
    lowered.includes("authenticat") ||
    lowered.includes("signed in") ||
    lowered.includes("permission denied") ||
    lowered.includes("login")
  );
}

async function graphql<T>(
  creds: Credentials,
  query: string,
  variables: Record<string, unknown> = {},
): Promise<T> {
  let lastError: unknown;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt += 1) {
    await throttle();

    let response: Response;
    try {
      response = await fetch(ENDPOINT, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          cookie: `LEETCODE_SESSION=${creds.session}; csrftoken=${creds.csrfToken}`,
          "x-csrftoken": creds.csrfToken,
          referer: "https://leetcode.com",
          "user-agent": "leetloop/1.0 (+https://github.com/yadava5/leetloop)",
        },
        body: JSON.stringify({ query, variables }),
      });
    } catch (error) {
      // Network-level failure: retry with backoff.
      lastError = error;
      const wait = 3 ** attempt * 1000;
      console.warn(
        `  [retry ${attempt + 1}/${MAX_RETRIES}] network error, waiting ${wait}ms`,
      );
      await sleep(wait);
      continue;
    }

    if (response.status === 401 || response.status === 403) {
      throw new SessionExpiredError(`HTTP ${response.status}`);
    }

    if (response.status === 429 || response.status >= 500) {
      const wait = 3 ** attempt * 1000;
      console.warn(
        `  [retry ${attempt + 1}/${MAX_RETRIES}] HTTP ${response.status}, waiting ${wait}ms`,
      );
      lastError = new Error(`HTTP ${response.status}`);
      await sleep(wait);
      continue;
    }

    const body = await response.text();
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${body.slice(0, 300)}`);
    }

    const payload = JSON.parse(body) as { data?: T; errors?: unknown[] };
    if (payload.errors && payload.errors.length > 0) {
      const detail = JSON.stringify(payload.errors).slice(0, 300);
      if (looksLikeAuthFailure(detail)) throw new SessionExpiredError(detail);
      throw new Error(`GraphQL errors: ${detail}`);
    }
    if (!payload.data) throw new Error("GraphQL response carried no data");
    return payload.data;
  }

  throw new Error(
    `exhausted ${MAX_RETRIES} attempts: ${lastError instanceof Error ? lastError.message : String(lastError)}`,
  );
}

const Q_USER_STATUS = `query { userStatus { isSignedIn username } }`;

const Q_SUBMISSION_LIST = `
query submissionList($offset: Int!, $limit: Int!) {
  submissionList(offset: $offset, limit: $limit) {
    hasNext
    submissions { id title titleSlug statusDisplay lang timestamp }
  }
}`;

const Q_SUBMISSION_DETAILS = `
query submissionDetails($submissionId: Int!) {
  submissionDetails(submissionId: $submissionId) {
    code timestamp
    runtimeDisplay runtimePercentile
    memoryDisplay memoryPercentile
    lang { verboseName }
  }
}`;

const Q_QUESTION = `
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId questionFrontendId title titleSlug difficulty
    topicTags { name slug }
    similarQuestions
  }
}`;

/**
 * Confirm the cookie is live before anything else runs.
 *
 * Without this, an expired cookie can present as an empty submission list,
 * which is indistinguishable from a quiet day. Checked explicitly instead.
 */
export async function assertSignedIn(creds: Credentials): Promise<string> {
  const data = await graphql<{
    userStatus: { isSignedIn: boolean; username: string | null };
  }>(creds, Q_USER_STATUS);
  if (!data.userStatus?.isSignedIn) {
    throw new SessionExpiredError(
      "authenticated query returned isSignedIn=false",
    );
  }
  return data.userStatus.username ?? "(unknown)";
}

/**
 * Accepted submissions newer than `sinceTimestamp`, latest per slug.
 *
 * At 4-10 solves/day one 20-row page covers a daily run, but the loop pages
 * anyway so a missed week still catches up.
 */
export async function fetchNewAccepted(
  creds: Credentials,
  sinceTimestamp: number,
  maxPages = 25,
): Promise<Map<string, SubmissionSummary>> {
  const latestPerSlug = new Map<string, SubmissionSummary>();
  let offset = 0;
  let reachedKnownHistory = false;

  for (let page = 0; page < maxPages && !reachedKnownHistory; page += 1) {
    const data = await graphql<{
      submissionList: {
        hasNext: boolean;
        submissions: SubmissionSummary[];
      } | null;
    }>(creds, Q_SUBMISSION_LIST, { offset, limit: 20 });

    const list = data.submissionList;
    if (!list) {
      // An authenticated field coming back null is an auth problem, not silence.
      throw new SessionExpiredError("submissionList returned null");
    }

    for (const submission of list.submissions) {
      const ts = Number(submission.timestamp);
      if (ts <= sinceTimestamp) {
        reachedKnownHistory = true;
        continue;
      }
      if (submission.statusDisplay !== "Accepted") continue;
      const existing = latestPerSlug.get(submission.titleSlug);
      if (!existing || Number(existing.timestamp) < ts) {
        latestPerSlug.set(submission.titleSlug, submission);
      }
    }

    if (!list.hasNext) break;
    offset += 20;
  }

  return latestPerSlug;
}

/** Latest accepted submission for one slug, regardless of lastSyncedTimestamp. */
export async function findLatestAcceptedForSlug(
  creds: Credentials,
  slug: string,
  maxPages = 25,
): Promise<SubmissionSummary | null> {
  let offset = 0;
  let best: SubmissionSummary | null = null;

  for (let page = 0; page < maxPages; page += 1) {
    const data = await graphql<{
      submissionList: {
        hasNext: boolean;
        submissions: SubmissionSummary[];
      } | null;
    }>(creds, Q_SUBMISSION_LIST, { offset, limit: 20 });
    const list = data.submissionList;
    if (!list) throw new SessionExpiredError("submissionList returned null");

    for (const submission of list.submissions) {
      if (submission.titleSlug !== slug) continue;
      if (submission.statusDisplay !== "Accepted") continue;
      if (!best || Number(best.timestamp) < Number(submission.timestamp))
        best = submission;
    }
    if (best || !list.hasNext) break;
    offset += 20;
  }

  return best;
}

export async function fetchSubmissionDetail(
  creds: Credentials,
  submissionId: string,
): Promise<SubmissionDetail> {
  const data = await graphql<{
    submissionDetails: {
      code: string | null;
      timestamp: number;
      runtimeDisplay: string | null;
      runtimePercentile: number | null;
      memoryDisplay: string | null;
      memoryPercentile: number | null;
      lang: { verboseName: string } | null;
    } | null;
  }>(creds, Q_SUBMISSION_DETAILS, { submissionId: Number(submissionId) });

  const detail = data.submissionDetails;
  if (!detail)
    throw new SessionExpiredError(
      `submissionDetails(${submissionId}) returned null`,
    );
  if (!detail.code || detail.code.trim() === "") {
    // Unauthenticated callers get metadata with no code, so empty code here
    // means the cookie is not being honoured.
    throw new SessionExpiredError(
      `submission ${submissionId} came back with empty code`,
    );
  }

  return {
    code: detail.code,
    timestamp: detail.timestamp,
    runtimeDisplay: detail.runtimeDisplay ?? "n/a",
    runtimePercentile: detail.runtimePercentile ?? null,
    memoryDisplay: detail.memoryDisplay ?? "n/a",
    memoryPercentile: detail.memoryPercentile ?? null,
    langVerbose: detail.lang?.verboseName ?? "unknown",
  };
}

/** Question metadata, with LeetCode's copyrighted prose dropped on the floor. */
export async function fetchQuestionMeta(
  creds: Credentials,
  slug: string,
): Promise<QuestionMeta> {
  const data = await graphql<{
    question: {
      questionId: string;
      questionFrontendId: string;
      title: string;
      titleSlug: string;
      difficulty: string;
      topicTags: { name: string; slug: string }[];
      similarQuestions: string | null;
    } | null;
  }>(creds, Q_QUESTION, { titleSlug: slug });

  const question = data.question;
  if (!question) throw new Error(`question(${slug}) returned null`);

  let similar: string[] = [];
  if (question.similarQuestions) {
    try {
      similar = (
        JSON.parse(question.similarQuestions) as { titleSlug: string }[]
      ).map((entry) => entry.titleSlug);
    } catch {
      similar = [];
    }
  }

  return {
    questionId: question.questionId,
    frontendId: question.questionFrontendId,
    title: question.title,
    slug: question.titleSlug,
    difficulty: question.difficulty,
    topics: question.topicTags.map((tag) => tag.name),
    similar,
  };
}
