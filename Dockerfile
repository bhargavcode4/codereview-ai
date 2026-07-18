FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY reviewer/ ./reviewer/
COPY run_review.py ingest_style_guide.py ./
COPY style_guide/ ./style_guide/

# GITHUB_EVENT_PATH, GITHUB_TOKEN, ANTHROPIC_API_KEY, SLACK_WEBHOOK_URL are
# provided at `docker run` time (Actions sets the first two automatically
# when this image is used as a workflow step).
ENTRYPOINT ["python", "run_review.py"]
