"""
DEMO: CodeReview AI - Complete Walkthrough
Shows the full pipeline without external API calls or heavy dependencies
"""

import json
import sys

# ============================================================================
# STEP 1: Simulate GitHub PR Event
# ============================================================================
print("\n" + "="*80)
print("🚀 STEP 1: GitHub Actions Triggers on Pull Request")
print("="*80)

github_event = {
    "action": "opened",
    "pull_request": {
        "number": 42,
        "title": "Add user authentication with password hashing",
        "html_url": "https://github.com/example/repo/pull/42",
        "state": "open"
    },
    "repository": {
        "name": "myapp",
        "owner": {"login": "teamname"}
    }
}

print(f"✅ PR Event received:")
print(f"   Repository: {github_event['repository']['owner']['login']}/{github_event['repository']['name']}")
print(f"   PR #{github_event['pull_request']['number']}: {github_event['pull_request']['title']}")
print(f"   URL: {github_event['pull_request']['html_url']}")


# ============================================================================
# STEP 2: Simulate github_client.py - Fetch Changed Files
# ============================================================================
print("\n" + "="*80)
print("📥 STEP 2: github_client.py → Fetch Changed Files from GitHub")
print("="*80)

files_from_github = [
    {
        "filename": "app/auth.py",
        "status": "modified",
        "patch": """@@ -10,15 +10,20 @@ def login(username, password):
     def login(username, password):
         # Check credentials
-        query = "SELECT * FROM users WHERE username = '" + username + "'"
+        query = "SELECT * FROM users WHERE username = %s"
         user = db.execute(query, (username,))
         
         if user and check_password(password, user['password']):
             return create_session(user['id'])
         return None
+
+def hash_password(pwd):
+    return hashlib.sha256(pwd.encode()).hexdigest()
+
+def check_password(pwd, hashed):
+    return hashlib.sha256(pwd.encode()).hexdigest() == hashed"""
    }
]

print(f"✅ Retrieved {len(files_from_github)} file(s) with diffs:")
for f in files_from_github:
    lines = f['patch'].count('\n')
    print(f"   • {f['filename']} ({f['status']}) - {lines} lines changed")


# ============================================================================
# STEP 3: Simulate rag.py - Retrieve Style Guide Context
# ============================================================================
print("\n" + "="*80)
print("🔍 STEP 3: rag.py → Retrieve Relevant Style Guide Chunks")
print("="*80)

# These are the actual chunks from example_style_guide.md
style_guide_chunks = [
    """## Security
- Never build SQL queries with string formatting or f-strings; use parameterized queries.
- Secrets (API keys, tokens, passwords) must come from environment variables or a secrets manager.
- Validate and sanitize all external input before using it.""",
    
    """## Python
- Use type hints on all public function signatures.
- Never catch bare `except:`; catch specific exceptions.
- Functions longer than ~40 lines should usually be split up.""",
]

print("📚 Style guide retrieved (top-2 relevant chunks):")
print("   CHUNK 1:")
for line in style_guide_chunks[0].split('\n'):
    print(f"      {line}")
print("\n   CHUNK 2:")
for line in style_guide_chunks[1].split('\n'):
    print(f"      {line}")


# ============================================================================
# STEP 4: Simulate llm_reviewer.py - Claude Analysis
# ============================================================================
print("\n" + "="*80)
print("🤖 STEP 4: llm_reviewer.py → Claude Analyzes Code + Style Context")
print("="*80)

# This simulates what Claude would return
review_issues = [
    {
        "file": "app/auth.py",
        "line": 13,
        "severity": "high",
        "comment": "Good fix! Using parameterized query prevents SQL injection. Matches 'use parameterized queries' from style guide."
    },
    {
        "file": "app/auth.py",
        "line": 21,
        "severity": "medium",
        "comment": "hash_password() should use bcrypt or argon2, not sha256. Sha256 is too fast for password hashing."
    },
    {
        "file": "app/auth.py",
        "line": 15,
        "severity": "low",
        "comment": "Missing type hints on function signature: def check_password(pwd, hashed). Add -> bool."
    }
]

print(f"✅ Claude found {len(review_issues)} issue(s):")
for i, issue in enumerate(review_issues, 1):
    severity_emoji = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
    print(f"\n   [{i}] {severity_emoji} Line {issue['line']} - {issue['severity'].upper()}")
    print(f"       {issue['comment']}")


# ============================================================================
# STEP 5: Filter by Severity & Prepare Comments
# ============================================================================
print("\n" + "="*80)
print("🎯 STEP 5: Filter Issues by MIN_SEVERITY_TO_POST")
print("="*80)

MIN_SEVERITY_TO_POST = "low"
SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}
min_sev = SEVERITY_ORDER.get(MIN_SEVERITY_TO_POST, 0)

filtered_issues = [i for i in review_issues 
                   if SEVERITY_ORDER.get(i.get("severity", "low"), 0) >= min_sev]

high_count = sum(1 for i in review_issues if i.get("severity") == "high")
print(f"Threshold: {MIN_SEVERITY_TO_POST}")
print(f"✅ {len(filtered_issues)} issue(s) will be posted (severity >= {MIN_SEVERITY_TO_POST})")
print(f"   • High severity: {high_count}")


# ============================================================================
# STEP 6: Simulate github_client.py - Post Comments
# ============================================================================
print("\n" + "="*80)
print("📝 STEP 6: github_client.py → Post Inline Comments on PR")
print("="*80)

comments_to_post = [
    {
        "path": "app/auth.py",
        "line": issue["line"],
        "side": "RIGHT",
        "body": f"**[{issue['severity'].upper()}]** {issue['comment']}"
    }
    for issue in filtered_issues
]

print(f"Posting to PR: {github_event['pull_request']['html_url']}")
print(f"Commit SHA: abc123def456...")
print(f"\n✅ {len(comments_to_post)} comment(s) will be posted:\n")

for comment in comments_to_post:
    print(f"   📌 Line {comment['line']}:")
    print(f"      {comment['body']}\n")


# ============================================================================
# STEP 7: Simulate slack_notify.py - Send Summary
# ============================================================================
print("="*80)
print("📢 STEP 7: slack_notify.py → Send Summary to Slack")
print("="*80)

summary = (
    f"🤖 **CodeReview AI**: reviewed 1 file, found {len(review_issues)} "
    f"issue(s) ({high_count} high severity)."
)

slack_payload = {
    "text": summary,
    "attachments": [
        {
            "color": "danger" if high_count > 0 else "warning",
            "title": f"PR Review: {github_event['pull_request']['title']}",
            "title_link": github_event['pull_request']['html_url'],
            "fields": [
                {"title": "Total Issues", "value": str(len(review_issues)), "short": True},
                {"title": "High Severity", "value": str(high_count), "short": True},
            ]
        }
    ]
}

print(f"🔗 Webhook: https://hooks.slack.com/services/XXX/YYY/ZZZ")
print(f"\n✅ Slack message:")
print(f"   {summary}\n")
print("   Details:")
for field in slack_payload["attachments"][0]["fields"]:
    print(f"   • {field['title']}: {field['value']}")


# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ PIPELINE COMPLETE!")
print("="*80)

pipeline_summary = f"""
CODEREVIEW AI EXECUTION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 🚀 GitHub Trigger
   → PR #{github_event['pull_request']['number']} opened

2. 📥 Fetch Files  
   → {len(files_from_github)} file(s) retrieved
   
3. 🔍 Retrieve Context
   → {len(style_guide_chunks)} style guide chunk(s) found
   
4. 🤖 Analyze Code
   → Claude reviewed with context
   → Found {len(review_issues)} issue(s)
   
5. 🎯 Filter Issues
   → Threshold: {MIN_SEVERITY_TO_POST}
   → {len(filtered_issues)} issue(s) pass threshold
   
6. 📝 Post Comments
   → Posted to GitHub PR (inline comments)
   
7. 📢 Slack Notification
   → Team notified via Slack

RESULT: PR review complete! All issues documented.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

print(pipeline_summary)


# ============================================================================
# BONUS: Show How RAG Grounding Works
# ============================================================================
print("\n" + "="*80)
print("🧠 BONUS: How RAG Grounding Prevents Generic Reviews")
print("="*80)

generic_review = """
WITHOUT RAG (Generic Review):
   "Fix SQL injection vulnerability"
   "Use better hashing algorithm"
   "Add type hints"
   
WITH RAG (Grounded Review):
   ✅ "Good fix! Using parameterized query prevents SQL injection. 
       Matches 'use parameterized queries' from style guide."
   ✅ "hash_password() should use bcrypt or argon2, not sha256. 
       Sha256 is too fast for password hashing."
   ✅ "Missing type hints on function signature. Add -> bool."

The RAG layer retrieves actual project rules and explains why
the code should change based on YOUR team's conventions.
"""

print(generic_review)
