import pymupdf

from targets.rag.chunking import chunk_text
from targets.rag.documents import load_document_from_file
from targets.rag.ingestion import ingest_document


# --------------------------------------------------
# Test 1: Real Markdown document
# --------------------------------------------------

document = load_document_from_file(
    "policy-1",
    "targets/rag/data/customer_policy.md",
)

chunks = chunk_text(
    document["content"],
    chunk_size=100,
    overlap=20,
)

print("\n" + "=" * 60)
print("TEST 1: Markdown document")
print("=" * 60)

for index, chunk in enumerate(chunks):
    print(f"\nChunk {index}:")
    print("Section:", chunk["section"])
    print("Length:", len(chunk["content"]))
    print("Content:", chunk["content"])


# --------------------------------------------------
# Test 2: Large paragraph
# --------------------------------------------------

large_text = """
# Security Policy

This is a deliberately long paragraph created to test whether our
chunker can split a paragraph that is larger than the configured
chunk size without breaking words into pieces. The paragraph contains
enough text that the chunker should produce multiple smaller chunks
while preserving the Security Policy section metadata.
"""

large_chunks = chunk_text(
    large_text,
    chunk_size=100,
    overlap=20,
)

print("\n" + "=" * 60)
print("TEST 2: Large paragraph")
print("=" * 60)

for index, chunk in enumerate(large_chunks):
    print(f"\nChunk {index}:")
    print("Section:", chunk["section"])
    print("Length:", len(chunk["content"]))
    print("Content:", chunk["content"])


# --------------------------------------------------
# Test 3: Generic ingestion with Markdown
# --------------------------------------------------

markdown_chunks = ingest_document(
    document_id="customer-policy",
    path="targets/rag/data/customer_policy.md",
    chunk_size=100,
    overlap=20,
)

print("\n" + "=" * 60)
print("TEST 3: Generic Markdown ingestion")
print("=" * 60)

print("\nTotal chunks:", len(markdown_chunks))

for index, chunk in enumerate(markdown_chunks):
    print(f"\nChunk {index}:")
    print("ID:", chunk["id"])
    print("Document ID:", chunk["document_id"])
    print("Metadata:", chunk["metadata"])
    print("Content:", chunk["content"])


# --------------------------------------------------
# Test 4: Generic ingestion with PDF
# --------------------------------------------------

pdf_path = "tests/test_policy.pdf"

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


pdf_chunks = ingest_document(
    document_id="customer-policy-pdf",
    path=pdf_path,
    chunk_size=100,
    overlap=20,
)

print("\n" + "=" * 60)
print("TEST 4: Generic PDF ingestion")
print("=" * 60)

print("\nTotal chunks:", len(pdf_chunks))

for index, chunk in enumerate(pdf_chunks):
    print(f"\nChunk {index}:")
    print("ID:", chunk["id"])
    print("Document ID:", chunk["document_id"])
    print("Metadata:", chunk["metadata"])
    print("Content:", chunk["content"])
