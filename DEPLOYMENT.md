# ⚡ CodeReview AI - Deployment Guide

## 🚀 Quick Deploy (3 Steps)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: CodeReview AI"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/codereview-ai.git
git push -u origin main
```

### Step 2: Add Repository Secrets
Go to: **Settings → Secrets and variables → Actions**

Add these secrets:
- `ANTHROPIC_API_KEY` = Your Claude API key from Anthropic
- `SLACK_WEBHOOK_URL` = (Optional) Slack webhook URL

`GITHUB_TOKEN` is provided automatically by GitHub Actions ✅

### Step 3: Create a Test PR
```bash
git checkout -b test-feature
# Make some code changes
git commit -am "Test changes"
git push origin test-feature
```
Then open a pull request on GitHub.

---

## 📊 Deployment Architecture

```
Your GitHub Repository
│
├─ .github/workflows/pr-review.yml  ← Workflow trigger
│  │
│  └─ On PR: opened, synchronize, reopened
│     │
│     ├─ Checkout code
│     ├─ Cache style guide index (Qdrant)
│     ├─ Setup Python 3.11
│     ├─ Install dependencies
│     ├─ Ingest style guide (if cache miss)
│     └─ Run run_review.py
│        │
│        └─ Posts inline PR comments
│           └─ Sends Slack notification
│
├─ requirements.txt  ← Dependencies
├─ run_review.py     ← Main script
├─ ingest_style_guide.py  ← Setup script
└─ style_guide/      ← Your conventions
```

---

## 🔧 GitHub Actions Workflow

The workflow (`.github/workflows/pr-review.yml`) automatically:

1. **Triggers** on every PR (opened, updated, reopened)
2. **Caches** the Qdrant index (only re-embedded if style guide changes)
3. **Installs** Python 3.11 + dependencies
4. **Ingests** style guide once
5. **Runs** the review pipeline
6. **Posts** inline comments on the PR
7. **Notifies** Slack with summary

### Workflow Benefits
✅ No server to host  
✅ Free GitHub Actions minutes  
✅ Automatic on every PR  
✅ Style guide caching (fast)  
✅ Runs in ~2-3 minutes per PR  

---

## 🐳 Alternative: Docker Deployment

### Build the Image
```bash
docker build -t codereview-ai:latest .
```

### Run Container
```bash
docker run \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e SLACK_WEBHOOK_URL=$SLACK_WEBHOOK_URL \
  -e GITHUB_EVENT_PATH=/tmp/event.json \
  -v $(pwd)/qdrant_data:/app/qdrant_data \
  -v /tmp/event.json:/tmp/event.json \
  codereview-ai:latest
```

### Use in GitHub Actions
```yaml
- name: Run CodeReview in Docker
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  uses: docker://codereview-ai:latest
```

---

## 🔐 Environment Variables Explained

| Variable | Source | Required | Purpose |
|----------|--------|----------|---------|
| `GITHUB_TOKEN` | Auto (`secrets.GITHUB_TOKEN`) | Yes | Fetch PR diffs, post comments |
| `ANTHROPIC_API_KEY` | Manual secret | Yes | Claude AI API key |
| `SLACK_WEBHOOK_URL` | Manual secret | No | Post summary to Slack |
| `GITHUB_EVENT_PATH` | Auto (Actions) | Yes | PR event payload path |
| `MIN_SEVERITY_TO_POST` | Env var (optional) | No | Filter: `low`, `medium`, `high` |
| `REVIEW_MODEL` | Env var (optional) | No | Default: `claude-sonnet-4-6` |

---

## 📝 Configuration: GitHub Secrets Setup

**Navigate to:** `Your Repo → Settings → Secrets and variables → Actions`

### Add Secret: ANTHROPIC_API_KEY
```
Name: ANTHROPIC_API_KEY
Secret: sk-ant-v7-xxxxxxxxxxxxxxxx
```
Get from: https://console.anthropic.com/keys

### Add Secret: SLACK_WEBHOOK_URL (Optional)
```
Name: SLACK_WEBHOOK_URL
Secret: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX
```
Get from: Slack → Your Workspace → Custom Integrations → Incoming Webhooks

---

## 🎯 What Happens After Deploy

### When PR is Opened:
```
1. GitHub detects pull_request event
   ↓
2. Workflow starts on ubuntu-latest
   ↓
3. CodeReview AI reviews changed files
   ↓
4. Inline comments appear on PR
   ↓
5. Slack message sent (if configured)
```

### PR Comment Example:
```
**[HIGH]** SQL injection risk! Use parameterized queries instead of string formatting.
This violates the "Security" rule in our style guide.
```

### Slack Notification Example:
```
🤖 CodeReview AI: reviewed 3 file(s), found 5 issue(s) (2 high severity).
Link: https://github.com/owner/repo/pull/42
```

---

## 🔄 Workflow Performance

| Step | Time | Notes |
|------|------|-------|
| Checkout | ~5s | Download repo |
| Cache restore | ~2s | Qdrant index (if cached) |
| Setup Python | ~10s | Install Python 3.11 |
| Install deps | ~30s | First run; faster if cached |
| Ingest guide | ~20s | Only if cache miss |
| Review | ~60s | ~20s per file on average |
| Post comments | ~5s | GitHub API |
| **Total** | **~2-3 min** | Typical PR with 3-5 files |

---

## ✅ Post-Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] `.github/workflows/pr-review.yml` present
- [ ] Secrets added: `ANTHROPIC_API_KEY`
- [ ] (Optional) Secrets added: `SLACK_WEBHOOK_URL`
- [ ] Test PR created and workflow runs
- [ ] Inline comments appear on PR
- [ ] (Optional) Slack message received

---

## 🐛 Troubleshooting

### Workflow shows red X
**Check:** Actions tab → View workflow run → See error logs

Common issues:
- Missing `ANTHROPIC_API_KEY` secret
- Invalid API key format
- Workflow file has YAML syntax error

### No inline comments on PR
**Check:** Workflow ran successfully but no comments?
- Possibly all issues filtered out by `MIN_SEVERITY_TO_POST`
- Check: Settings → Permissions → Ensure `pull-requests: write`

### Comments posted but Slack silent
**Check:** 
- `SLACK_WEBHOOK_URL` not set (optional, safe to skip)
- Invalid webhook URL format
- Webhook URL expired or revoked

### Slow workflow (>5 min)
**Optimize:**
- Check Actions cache settings
- Reduce style guide file size
- Limit files reviewed with path filters

---

## 📚 Additional Resources

| Resource | Link |
|----------|------|
| GitHub Actions Docs | https://docs.github.com/actions |
| Anthropic API | https://docs.anthropic.com |
| Qdrant Docs | https://qdrant.tech/documentation |
| Slack Webhooks | https://api.slack.com/messaging/webhooks |

---

## 🎓 Next Steps

1. **Customize Style Guide**
   - Edit `style_guide/example_style_guide.md`
   - Add your team's conventions
   - Commit and push

2. **Tune Review Criteria**
   - Edit `llm_reviewer.SYSTEM_PROMPT` for strictness
   - Test with real PRs
   - Iterate based on feedback

3. **Monitor & Improve**
   - Watch workflow runs in Actions tab
   - Gather feedback from team
   - Adjust `MIN_SEVERITY_TO_POST` threshold
   - Update style guide rules based on PRs reviewed

---

**🚀 Ready to deploy? Follow the "Quick Deploy (3 Steps)" above!**
