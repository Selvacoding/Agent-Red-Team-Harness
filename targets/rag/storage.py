import json
from pathlib import Path
from uuid import uuid4

import chromadb

from targets.rag.embeddings import create_embedding


class ChromaVectorStore:
    """Persistent local vector store with isolated default collections."""

    def __init__(
        self,
        collection_name: str | None = None,
        persist_directory: str = "data/chroma",
    ):
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_directory)

        # Each store gets its own collection unless sharing is explicitly
        # requested by supplying a collection_name.
        self.collection_name = collection_name or f"rag-{uuid4().hex}"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # Track IDs added by this instance so reset does not drop the
        # entire collection or delete another experiment's unrelated data.
        self._owned_ids: set[str] = set()

    def add_chunks(self, chunks: list[dict]) -> None:
        if not chunks:
            return

        self.collection.upsert(
            ids=[chunk["id"] for chunk in chunks],
            documents=[chunk["content"] for chunk in chunks],
            embeddings=[
                create_embedding(chunk["content"])
                for chunk in chunks
            ],
            metadatas=[
                {
                    "document_id": chunk["document_id"],
                    "metadata_json": json.dumps(chunk["metadata"]),
                }
                for chunk in chunks
            ],
        )

        self._owned_ids.update(chunk["id"] for chunk in chunks)

    def search(self, query: str, top_k: int = 2) -> list[dict]:
        count = self.collection.count()
        if count == 0 or top_k <= 0:
            return []

        results = self.collection.query(
            query_embeddings=[create_embedding(query)],
            n_results=min(top_k, count),
            include=["documents", "metadatas", "distances"],
        )

        matches = []
        for index, content in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][index]
            matches.append(
                {
                    "id": results["ids"][0][index],
                    "document_id": metadata["document_id"],
                    "content": content,
                    "metadata": json.loads(metadata["metadata_json"]),
                    "score": 1.0 - results["distances"][0][index],
                }
            )

        return matches

    def delete_document(self, document_id: str) -> None:
        results = self.collection.get(
            where={"document_id": document_id},
        )
        ids = results["ids"]

        if ids:
            self.collection.delete(ids=ids)
            self._owned_ids.difference_update(ids)

    def reset(self) -> None:
        """Delete this instance's tracked chunks, not the whole collection."""
        if self._owned_ids:
            self.collection.delete(ids=list(self._owned_ids))
            self._owned_ids.clear()
