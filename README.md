# CodeReview AI

An agent that reviews pull requests automatically: it reads the diff, grounds its
opinions in your team's style guide via a RAG layer, flags bugs/style/security issues,
posts inline PR comments, and pings Slack with a summary.

## Why it's simple

The original spec called for a FastAPI webhook server + GitHub App + persistent
deployment. This version gets the same result with far less infrastructure:
**GitHub Actions *is* the webhook receiver.** Every `pull_request` event already
comes with the full payload (`GITHUB_EVENT_PATH`) and a scoped token
(`secrets.GITHUB_TOKEN`) for free. No server to host, no ngrok, no GitHub App to
register. You still get a real agentic pipeline underneath -- just triggered
differently.

## Architecture

```
pull_request event (GitHub Actions)
        |
        v
run_review.py
        |
        |--> github_client.py   -- fetch changed files + diffs via GitHub REST API
        |
        |--> rag.py             -- embed diff context, retrieve relevant style-guide
        |                          chunks from an embedded (serverless) Qdrant index
        |
        |--> llm_reviewer.py    -- per-file prompt to Claude, diff + retrieved context,
        |                          structured JSON output (file, line, severity, comment)
        |
        |--> github_client.py   -- post inline review comments back to the PR
        |
        +--> slack_notify.py    -- post a run summary to a Slack webhook
```

Qdrant runs in **embedded mode** (`QdrantClient(path=...)`) -- no separate
container or hosted cluster needed, which is what actually makes "Dockerize +
deploy" tractable for a side project. Embeddings are local via
`sentence-transformers`, so ingesting a style guide costs no API calls.

## Setup

1. **Fork/clone this into the repo you want reviewed** (or copy the `reviewer/`
   package, `run_review.py`, `ingest_style_guide.py`, and
   `.github/workflows/pr-review.yml` into an existing repo).
2. Add repo secrets: `Settings -> Secrets and variables -> Actions`
   - `ANTHROPIC_API_KEY`
   - `SLACK_WEBHOOK_URL` (optional -- skipped if unset)
   - `GITHUB_TOKEN` is provided automatically, no need to add it.
3. Replace `style_guide/example_style_guide.md` with your actual conventions, or point
   `ingest_style_guide.py` at a folder of past PR review comments instead.
4. Open a PR against the repo. The `CodeReview AI` workflow runs automatically and
   posts inline comments + a Slack summary.

## Running locally (for testing/demo before opening real PRs)

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
export $(cat .env | xargs)

# 1. Seed the style guide index once
python ingest_style_guide.py style_guide/example_style_guide.md

# 2. Simulate a GitHub Actions run against a real open PR:
#    save the PR's webhook-shaped payload to a file and point GITHUB_EVENT_PATH at it.
#    Easiest way: `gh api repos/OWNER/REPO/pulls/NUMBER` won't match the webhook shape
#    exactly, so for local testing it's simplest to just open a real test PR and let
#    Actions run it -- or adapt run_review.py's load_event() to call
#    github_client.get_pr_files() directly with a hardcoded owner/repo/pr_number.
```

The straightforward path is: push to a scratch branch, open a PR against a
throwaway test repo, and watch the Action run end-to-end. That's also your demo
recording.

## Tuning

- `MIN_SEVERITY_TO_POST` (env var, default `low`) controls the noise floor for
  inline comments.
- `llm_reviewer.SYSTEM_PROMPT` is the single place to tighten the review criteria
  if you're seeing false positives -- iterate on it against 5-10 real PRs before
  calling it done.
- Line numbers in inline comments are best-effort (mapped from the diff hunk by the
  LLM). If GitHub rejects a comment because the line isn't part of the diff, the
  whole review falls back to a summary-only comment rather than failing the run.

## What this demonstrates

- Agentic pipeline with tool-calling-style structured output (diff in, JSON issues out)
- RAG grounding (Qdrant + sentence-transformers) to reduce generic/false-positive review
  comments
- GitHub REST API integration (diffs in, inline review comments out)
- CI/CD-native deployment (GitHub Actions as both trigger and runtime, no hosting)
- Slack integration for run visibility

## Stretch goals (not required for the MVP)

- Swap Actions-trigger for a real FastAPI webhook + GitHub App if you want reviews to
  also run outside CI (e.g. on draft PRs, or across many external repos).
- Track false-positive rate over time by having reviewers react 👎 on bad comments and
  logging it.
- Batch the RAG ingestion to run only when `style_guide/` changes (already handled by
  the Actions cache key on `hashFiles('style_guide/**')`).
