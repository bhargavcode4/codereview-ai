"""
Entry point executed by GitHub Actions on every `pull_request` event.

Reads the PR context from GITHUB_EVENT_PATH (the full webhook payload Actions
provides for free -- no GitHub App or public webhook endpoint required),
fetches the diff, runs the RAG-grounded LLM review, posts inline PR comments,
and pings Slack with a summary.
"""
import json
import os

from reviewer import config, github_client, llm_reviewer, rag, slack_notify

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}


def load_event():
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        return json.load(f)


def main():
    event = load_event()
    pr = event["pull_request"]
    owner = event["repository"]["owner"]["login"]
    repo = event["repository"]["name"]
    pr_number = pr["number"]

    print(f"Reviewing PR #{pr_number} in {owner}/{repo}...")
    files = github_client.get_pr_files(owner, repo, pr_number)
    print(f"{len(files)} changed file(s) with a reviewable diff.")

    min_sev = SEVERITY_ORDER.get(config.MIN_SEVERITY_TO_POST, 0)
    all_comments, all_issues = [], []

    for f in files:
        query = f["filename"] + "\n" + f["patch"][:500]
        style_context = "\n---\n".join(rag.retrieve(query, top_k=3))

        issues = llm_reviewer.review_file_diff(f["filename"], f["patch"], style_context)
        all_issues.extend(issues)

        for issue in issues:
            if SEVERITY_ORDER.get(issue.get("severity", "low"), 0) < min_sev:
                continue
            all_comments.append(
                {
                    "path": issue["file"],
                    "line": issue["line"],
                    "side": "RIGHT",
                    "body": f"**[{issue['severity'].upper()}]** {issue['comment']}",
                }
            )

    high_count = sum(1 for i in all_issues if i.get("severity") == "high")
    summary = (
        f"🤖 **CodeReview AI**: reviewed {len(files)} file(s), found {len(all_issues)} "
        f"issue(s) ({high_count} high severity)."
    )

    if all_comments:
        github_client.post_review(owner, repo, pr_number, all_comments, summary)
    else:
        print("No issues met the posting threshold; skipping inline review.")

    slack_notify.post_summary(pr["title"], pr["html_url"], len(all_issues), high_count, len(files))
    print("Done.")


if __name__ == "__main__":
    main()
