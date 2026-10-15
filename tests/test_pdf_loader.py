import pymupdf

from targets.rag.pdf_loader import (
    load_pdf,
    chunk_pdf_pages,
)


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


pages = load_pdf(pdf_path)

print("\n" + "=" * 60)
print("PDF LOADER TEST")
print("=" * 60)

print("\nExtracted pages:\n")

for page in pages:
    print(f"\nPage {page['page']}:")
    print(page["text"])


chunks = chunk_pdf_pages(
    pages,
    chunk_size=100,
    overlap=20,
)

print("\n" + "=" * 60)
print("PDF → CHUNKER TEST")
print("=" * 60)

for index, chunk in enumerate(chunks):

    print(f"\nChunk {index}:")
    print("Section:", chunk["section"])
    print("Source:", chunk["metadata"]["source"])
    print("Page:", chunk["metadata"]["page"])
    print("Chunk index:", chunk["metadata"]["chunk_index"])
    print("Length:", len(chunk["content"]))
    print("Content:", chunk["content"])
