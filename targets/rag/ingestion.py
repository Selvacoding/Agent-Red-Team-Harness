from pathlib import Path

from targets.rag.chunking import chunk_text
from targets.rag.pdf_loader import chunk_pdf_pages, load_pdf


def ingest_text_content(
    document_id: str,
    content: str,
    chunk_size: int = 200,
    overlap: int = 50,
) -> list[dict]:

    chunks = chunk_text(
        content,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    results = []

    for chunk_index, chunk in enumerate(chunks):

        results.append({
            "id": f"{document_id}-chunk-{chunk_index}",
            "document_id": document_id,
            "content": chunk["content"],
            "metadata": {
                "source": document_id,
                "section": chunk["section"],
                "chunk_index": chunk_index,
            },
        })

    return results


def ingest_text_document(
    document_id: str,
    content: str,
    chunk_size: int = 200,
    overlap: int = 50,
) -> list[dict]:

    return ingest_text_content(
        document_id=document_id,
        content=content,
        chunk_size=chunk_size,
        overlap=overlap,
    )


def ingest_pdf_document(
    document_id: str,
    path: str,
    chunk_size: int = 200,
    overlap: int = 50,
) -> list[dict]:

    pages = load_pdf(path)

    chunks = chunk_pdf_pages(
        pages,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    results = []

    for chunk_index, chunk in enumerate(chunks):

        results.append({
            "id": f"{document_id}-chunk-{chunk_index}",
            "document_id": document_id,
            "content": chunk["content"],
            "metadata": {
                "source": chunk["metadata"]["source"],
                "page": chunk["metadata"]["page"],
                "section": chunk["section"],
                "chunk_index": chunk_index,
            },
        })

    return results


def ingest_document(
    document_id: str,
    path: str,
    chunk_size: int = 200,
    overlap: int = 50,
) -> list[dict]:

    extension = Path(path).suffix.lower()

    if extension == ".pdf":
        return ingest_pdf_document(
            document_id=document_id,
            path=path,
            chunk_size=chunk_size,
            overlap=overlap,
        )

    if extension in {".txt", ".md"}:

        content = Path(path).read_text(
            encoding="utf-8"
        )

        return ingest_text_content(
            document_id=document_id,
            content=content,
            chunk_size=chunk_size,
            overlap=overlap,
        )

    raise ValueError(
        f"Unsupported document type: {extension}"
    )
