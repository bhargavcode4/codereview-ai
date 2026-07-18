"""
Embed your style guide / past-review notes into Qdrant so the reviewer can
ground its comments in project conventions.

Usage:
    python ingest_style_guide.py style_guide/example_style_guide.md [more.md ...]
"""
import sys

from reviewer import rag


def chunk_text(text: str, max_chars: int = 800) -> list:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if len(current) + len(p) > max_chars:
            if current:
                chunks.append(current)
            current = p
        else:
            current += ("\n\n" if current else "") + p
    if current:
        chunks.append(current)
    return chunks


def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_style_guide.py <file1.md> [file2.md ...]")
        sys.exit(1)

    all_chunks = []
    for path in sys.argv[1:]:
        with open(path) as f:
            text = f.read()
        chunks = chunk_text(text)
        print(f"{path}: {len(chunks)} chunk(s)")
        all_chunks.extend(chunks)

    rag.ingest_documents(all_chunks)
    print(f"Ingested {len(all_chunks)} chunk(s) into Qdrant collection '{rag.config.COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()
