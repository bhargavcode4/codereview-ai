import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

QDRANT_PATH = os.environ.get("QDRANT_PATH", "./qdrant_data")
COLLECTION_NAME = "style_guide"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").lower()
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
REVIEW_MODEL = os.environ.get("REVIEW_MODEL", DEFAULT_GROQ_MODEL if LLM_PROVIDER == "groq" else DEFAULT_ANTHROPIC_MODEL)
MAX_DIFF_CHARS_PER_FILE = 6000

# Minimum severity that gets posted as an inline PR comment: "low" | "medium" | "high"
MIN_SEVERITY_TO_POST = os.environ.get("MIN_SEVERITY_TO_POST", "low")
