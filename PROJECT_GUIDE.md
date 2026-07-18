# CodeReview AI - Project Overview & Architecture

## What It Does
CodeReview AI is an automated pull request reviewer that:
1. **Reads PR diffs** automatically when triggered by GitHub Actions
2. **Grounds reviews** in your team's style guide using RAG (Retrieval-Augmented Generation)
3. **Analyzes code** for bugs, security issues, and style violations using Claude AI
4. **Posts inline comments** directly on the PR for specific lines
5. **Notifies Slack** with a summary of findings

## Key Features

### ✅ No Infrastructure Required
- Uses **GitHub Actions as the webhook receiver** (no custom server needed)
- Qdrant runs in **embedded mode** (on-disk, serverless)
- Embeddings generated locally via `sentence-transformers` (no API calls)

### 🎯 RAG-Grounded Reviews
The system doesn't just use generic Claude prompts. It:
1. **Retrieves** relevant chunks from your style guide
2. **Embeds** them into a vector database
3. **Augments** the review prompt with project-specific context
4. Result: Reviews that align with YOUR conventions, not generic rules

### 🏗️ Agentic Pipeline
```
PR Event (GitHub Actions)
    ↓
github_client.py      → Fetch changed files and diffs from GitHub API
    ↓
rag.py                → Embed diff context, retrieve relevant style guide chunks
    ↓
llm_reviewer.py       → Claude analyzes each file, returns structured JSON issues
    ↓
github_client.py      → Post inline review comments on the PR
    ↓
slack_notify.py       → Send summary notification to Slack
```

## Project Structure

| File | Purpose |
|------|---------|
| `run_review.py` | Main entry point - orchestrates the entire review pipeline |
| `ingest_style_guide.py` | One-time setup: indexes your style guide into Qdrant |
| `reviewer/config.py` | Configuration from environment variables |
| `reviewer/github_client.py` | GitHub REST API integration (fetch diffs, post comments) |
| `reviewer/llm_reviewer.py` | Claude AI integration for code analysis |
| `reviewer/rag.py` | Qdrant vector database for style guide retrieval |
| `reviewer/slack_notify.py` | Optional Slack webhook notifications |

## How to Use

### 1. Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your keys (see .env.example)
cp .env.example .env
# Edit .env with your:
#   - ANTHROPIC_API_KEY
#   - GITHUB_TOKEN (for local testing)
#   - SLACK_WEBHOOK_URL (optional)

# Index your style guide once
python ingest_style_guide.py style_guide/example_style_guide.md
```

### 2. Local Testing (Before Real Deployment)
```bash
# Set environment
export $(cat .env | xargs)
export GITHUB_EVENT_PATH=test_event.json

# Run the review
python run_review.py
```

### 3. GitHub Actions Deployment
Add this workflow file at `.github/workflows/pr-review.yml` to trigger on every PR.
The workflow automatically provides:
- `GITHUB_TOKEN` via `secrets.GITHUB_TOKEN`
- `GITHUB_EVENT_PATH` pointing to the PR payload

## Configuration Options

| Env Variable | Default | Purpose |
|--------------|---------|---------|
| `ANTHROPIC_API_KEY` | - | Required: Claude API key |
| `GITHUB_TOKEN` | - | Required: GitHub API authentication |
| `SLACK_WEBHOOK_URL` | - | Optional: Post summaries to Slack |
| `MIN_SEVERITY_TO_POST` | `low` | Only post comments at this severity or higher |
| `REVIEW_MODEL` | `claude-sonnet-4-6` | Which Claude model to use |
| `QDRANT_PATH` | `./qdrant_data` | Where to store the vector database |

## Review Output Format

The LLM returns structured JSON for each issue:
```json
{
  "file": "src/utils.py",
  "line": 42,
  "severity": "high|medium|low",
  "comment": "Bare except clause catches SystemExit. Use specific exception type."
}
```

Issues are then posted as inline comments on the PR with format:
```
**[HIGH]** Bare except clause catches SystemExit. Use specific exception type.
```

## Style Guide Example

The project includes `style_guide/example_style_guide.md` with rules for:
- **Python**: Type hints, pathlib usage, exception handling
- **Security**: No hardcoded secrets, parameterized queries, input validation
- **API Design**: Schema validation, structured errors, versioning
- **Git Hygiene**: Commit messages, no dead code, tests required

These rules are embedded into the vector database and used to augment review prompts.

## Key Design Decisions

1. **GitHub Actions as Webhook**: Eliminates need for a hosted server
2. **Embedded Qdrant**: No separate database deployment
3. **Local Embeddings**: No embedding API costs
4. **Structured JSON Output**: Reliable parsing, easier to extend
5. **Fallback Logic**: If line numbers are wrong, posts summary-only review instead of failing

## Architecture Benefits

✅ **Minimal Operations**: Everything runs in GitHub Actions or locally  
✅ **Cost Efficient**: One Claude API call per file reviewed  
✅ **Customizable**: RAG layer grounds reviews in YOUR style guide  
✅ **Transparent**: Structured JSON output is easy to parse and extend  
✅ **Graceful Degradation**: Handles edge cases without hard failures
