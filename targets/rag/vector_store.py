from targets.rag.documents import documents
from targets.rag.embeddings import create_embedding
from targets.rag.similarity import cosine_similarity
from targets.rag.ingestion import (
    ingest_document,
    ingest_text_content,
)

vector_store = []

def add_document_to_vector_store(
    document_id: str,
    path: str,
    chunk_size: int = 200,
    overlap: int = 50,
) -> None:

    chunks = ingest_document(
        document_id=document_id,
        path=path,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    add_chunks_to_vector_store(chunks)


def add_chunks_to_vector_store(
    chunks: list[dict],
) -> None:

    for chunk in chunks:

        embedding = create_embedding(
            chunk["content"]
        )

        vector_store.append({
            "id": chunk["id"],
            "document_id": chunk["document_id"],
            "content": chunk["content"],
            "metadata": {
                **chunk["metadata"],
            },
            "embedding": embedding,
        })


def build_vector_store() -> None:
    vector_store.clear()

    for document in documents:

        chunks = ingest_text_content(
            document_id=document["id"],
            content=document["content"],
        )

        add_chunks_to_vector_store(chunks)


def reset_vector_store() -> None:
    build_vector_store()


def search(
    query: str,
    top_k: int = 2,
) -> list[dict]:

    query_embedding = create_embedding(query)

    scored_documents = []

    for document in vector_store:

        similarity = cosine_similarity(
            query_embedding,
            document["embedding"],
        )

        scored_documents.append({
            "id": document["id"],
            "document_id": document["document_id"],
            "content": document["content"],
            "metadata": document["metadata"],
            "score": similarity,
        })

    scored_documents.sort(
        key=lambda document: document["score"],
        reverse=True,
    )

    return scored_documents[:top_k]

def add_document_to_persistent_store(
    store,
    document_id: str,
    path: str,
    chunk_size: int = 200,
    overlap: int = 50,
) -> None:
    chunks = ingest_document(
        document_id=document_id,
        path=path,
        chunk_size=chunk_size,
        overlap=overlap,
    )
    store.add_chunks(chunks)


def add_chunks_to_persistent_store(store, chunks: list[dict]) -> None:
    store.add_chunks(chunks)
