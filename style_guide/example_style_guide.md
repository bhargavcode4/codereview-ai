# Project Style Guide (example)

Replace this file with your team's real conventions -- or point ingest_style_guide.py
at a folder of past PR review comments instead. The RAG layer just needs text chunks.

## Python

- Use type hints on all public function signatures.
- Prefer `pathlib.Path` over `os.path` for filesystem paths.
- Never catch bare `except:`; catch specific exceptions.
- Log with the `logging` module, not `print`, in application code (scripts are fine).
- Functions longer than ~40 lines should usually be split up.

## Security

- Never build SQL queries with string formatting or f-strings; use parameterized queries.
- Secrets (API keys, tokens, passwords) must come from environment variables or a secrets
  manager, never hardcoded or committed.
- Validate and sanitize all external input (query params, request bodies, file uploads)
  before using it.

## API design

- All new endpoints must validate request bodies with a schema (e.g. Pydantic).
- Return structured error responses with a machine-readable `code` field, not just a
  free-text message.
- Breaking changes to existing endpoints require a version bump.

## Git / PR hygiene

- Commit messages should explain *why*, not just *what*.
- No commented-out code blocks left in merged PRs.
- Tests are required for new business logic; pure refactors are exempt.
