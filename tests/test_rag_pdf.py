from targets.rag.agent import RAGAgent


agent = RAGAgent(
    document_id="customer-policy-pdf",
    document_path="tests/test_policy.pdf",
)


result = agent.run(
    "What is the customer deletion policy?"
)


print("\nResponse:")
print(result.response)

print("\nRetrieved:")

for document in result.rag_execution.retrieved_documents:
    print(
        document["metadata"],
        "→",
        document["content"],
    )
    