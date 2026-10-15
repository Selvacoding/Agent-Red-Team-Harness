from pathlib import Path

import pymupdf

from targets.rag.chunking import chunk_text


def load_pdf(path: str) -> list[dict]:

    document = pymupdf.open(path)

    source = Path(path).name

    pages = []

    for page_number, page in enumerate(document, start=1):
        pages.append({
            "page": page_number,
            "source": source,
            "text": page.get_text(),
        })

    document.close()

    return pages


def chunk_pdf_pages(
    pages: list[dict],
    chunk_size: int = 200,
    overlap: int = 50,
) -> list[dict]:

    chunks = []

    for page in pages:

        page_chunks = chunk_text(
            page["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_index, chunk in enumerate(page_chunks):

            chunks.append({
                "content": chunk["content"],
                "section": chunk["section"],
                "metadata": {
                    "source": page["source"],
                    "page": page["page"],
                    "chunk_index": chunk_index,
                },
            })

    return chunks
