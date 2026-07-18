import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

QDRANT_PATH = os.environ.get("QDRANT_PATH", "./qdrant_data")
COLLECTION_NAME = "style_guide"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

REVIEW_MODEL = os.environ.get("REVIEW_MODEL", "claude-sonnet-4-6")
MAX_DIFF_CHARS_PER_FILE = 6000

# Minimum severity that gets posted as an inline PR comment: "low" | "medium" | "high"
MIN_SEVERITY_TO_POST = os.environ.get("MIN_SEVERITY_TO_POST", "low")
