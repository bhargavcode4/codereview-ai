import requests

from . import config


def post_summary(pr_title: str, pr_url: str, issue_count: int, high_count: int, files_reviewed: int):
    if not config.SLACK_WEBHOOK_URL:
        print("No SLACK_WEBHOOK_URL set, skipping Slack notification.")
        return

    text = (
        f"*CodeReview AI* reviewed <{pr_url}|{pr_title}>\n"
        f"Files reviewed: {files_reviewed} | Issues found: {issue_count} "
        f"({high_count} high severity)"
    )
    resp = requests.post(config.SLACK_WEBHOOK_URL, json={"text": text})
    if resp.status_code >= 300:
        print(f"Slack post failed ({resp.status_code}): {resp.text[:300]}")
