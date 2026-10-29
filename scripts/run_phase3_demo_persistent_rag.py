from pathlib import Path

from targets.rag.agent import RAGAgent
from targets.rag.storage import ChromaVectorStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_PATH = (
    PROJECT_ROOT / "targets" / "rag" / "data" / "customer_policy.md"
)
DB_PATH = PROJECT_ROOT / ".local-data" / "chroma"
COLLECTION_NAME = "phase3-customer-policy-demo"


def main() -> None:
    if not DOCUMENT_PATH.exists():
        raise FileNotFoundError(DOCUMENT_PATH)

    print("=== Persistent Chroma RAG Demo ===")
    print(f"Document: {DOCUMENT_PATH}")
    print(f"Database: {DB_PATH}")
    print(f"Collection: {COLLECTION_NAME}")

    # Open (or create) a persistent Chroma collection.
    store = ChromaVectorStore(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_PATH),
    )

    # Remove only this document's previous chunks before re-ingesting it.
    store.delete_document("customer-policy")

    # Ingest the real document into Chroma and query it using local Ollama.
    agent = RAGAgent(
        document_id="customer-policy",
        document_path=str(DOCUMENT_PATH),
        persistent_store=store,
    )

    print(f"\nChunks stored: {store.collection.count()}")

    question = "Summarize the important customer policy rules."
    print(f"\nQuestion: {question}")

    result = agent.run(question)

    print("\n=== Retrieved Evidence ===")
    for index, doc in enumerate(result.rag_execution.retrieved_documents, 1):
        print(f"\n[{index}] Document: {doc['document_id']}")
        print(f"Chunk ID: {doc['id']}")
        print(f"Similarity score: {doc['score']:.4f}")
        print(doc["content"])

    print("\n=== Local LLM Answer ===")
    print(result.response)

    # Reopen the same on-disk database through a second client.
    reopened_store = ChromaVectorStore(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_PATH),
    )

    print("\n=== Persistence Verification ===")
    print(f"Original client count: {store.collection.count()}")
    print(f"Reopened client count: {reopened_store.collection.count()}")

    persisted_docs = reopened_store.search(
        "customer policy rules",
        top_k=2,
    )
    print(f"Results after reopening: {len(persisted_docs)}")

    if not persisted_docs:
        raise RuntimeError("Persistence verification failed: no results.")

    print("\nPASS: Chroma data is available after reopening the database.")


if __name__ == "__main__":
    main()
