from targets.rag.documents import add_document
from targets.rag.embeddings import create_embedding
from targets.rag.chunking import chunk_text
from targets.rag.vector_store import vector_store


def poison_document(content: str) -> None:
    document = {
        "id": "poisoned-document",
        "content": content,
    }

    add_document(document)

    chunks = chunk_text(content)

    for index, chunk in enumerate(chunks):
        content = chunk["content"]

        embedding = create_embedding(content)

        vector_store.append({
            "id": f"{document['id']}-chunk-{index}",
            "document_id": document["id"],
            "content": content,
            "metadata": {
                "source": document["id"],
                "section": chunk["section"],
                "chunk_index": index,
                "poisoned": True,
            },
            "embedding": embedding,
        })
