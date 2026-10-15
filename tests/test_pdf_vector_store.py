import pymupdf

from targets.rag.vector_store import (
    vector_store,
    reset_vector_store,
    add_document_to_vector_store,
    search,
)


pdf_path = "tests/test_policy.pdf"


# --------------------------------------------------
# Create test PDF
# --------------------------------------------------

document = pymupdf.open()

page = document.new_page()

page.insert_text(
    (72, 72),
    "Customer Support Policy\n\n"
    "Customer information can be retrieved only "
    "for legitimate support requests."
)

page = document.new_page()

page.insert_text(
    (72, 72),
    "Customer Deletion Policy\n\n"
    "Customer deletion requires explicit "
    "authorization from an administrator."
)

document.save(pdf_path)
document.close()


# --------------------------------------------------
# Reset vector store
# --------------------------------------------------

reset_vector_store()


# --------------------------------------------------
# Add PDF to vector store
# --------------------------------------------------

add_document_to_vector_store(
    document_id="customer-policy-pdf",
    path=pdf_path,
    chunk_size=100,
    overlap=20,
)


# --------------------------------------------------
# Print vector store
# --------------------------------------------------

print("\n" + "=" * 60)
print("PDF → VECTOR STORE")
print("=" * 60)

print("\nTotal vectors:", len(vector_store))

for document in vector_store:
    print("\nID:", document["id"])
    print("Document ID:", document["document_id"])
    print("Metadata:", document["metadata"])
    print("Content:", document["content"])


# --------------------------------------------------
# Test retrieval
# --------------------------------------------------

results = search(
    "What is the customer deletion policy?"
)


print("\n" + "=" * 60)
print("PDF → VECTOR STORE → RETRIEVAL")
print("=" * 60)

for index, result in enumerate(results):

    print(f"\nResult {index}:")
    print("ID:", result["id"])
    print("Score:", result["score"])
    print("Metadata:", result["metadata"])
    print("Content:", result["content"])
