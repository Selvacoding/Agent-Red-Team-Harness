from targets.rag.documents import reset_documents
from targets.rag.vector_store import reset_vector_store, vector_store
from targets.rag.retriever import retrieve
from targets.rag.documents import documents

reset_documents()
print("Documents:", documents)
reset_vector_store()

print("Vector store size:", len(vector_store))


results = retrieve(
    "What is the customer deletion policy?"
)


print("\nRetrieved chunks:")

for result in results:
    print("\nChunk ID:", result["id"])
    print("Document ID:", result["document_id"])
    print("Content:", result["content"])
    print("Metadata:", result["metadata"])
    print("Score:", result["score"])