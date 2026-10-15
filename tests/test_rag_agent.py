from targets.rag.agent import RAGAgent


agent = RAGAgent(
    document_id="customer-policy",
    document_path="targets/rag/data/customer_policy.md",
)


result = agent.run(
    "What is the customer deletion policy?"
)


print("\n" + "=" * 60)
print("RAG AGENT TEST")
print("=" * 60)

print("\nResponse:")
print(result.response)

print("\n" + "=" * 60)
print("RETRIEVED DOCUMENTS")
print("=" * 60)

for document in result.rag_execution.retrieved_documents:

    print("\nID:", document["id"])
    print("Score:", document["score"])
    print("Metadata:", document["metadata"])
    print("Content:", document["content"])
    