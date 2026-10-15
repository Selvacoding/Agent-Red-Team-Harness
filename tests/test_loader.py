from targets.rag.loader import load_text_file
from targets.rag.documents import load_document_from_file


text = load_text_file(
    "targets/rag/data/customer_policy.md"
)

document = load_document_from_file(
    "policy-1",
    "targets/rag/data/customer_policy.md",
)

print("\nDocument object:")
print(document)


print("\nLoaded document:\n")
# print(text)
