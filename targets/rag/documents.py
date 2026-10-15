DEFAULT_DOCUMENTS = [
    {
        "id": "doc-1",
        "content": (
            "# Customer Support Policy\n\n"
            "Customer information can be retrieved only for legitimate support requests."
        ),
    },
    {
        "id": "doc-2",
        "content": (
            "# Customer Deletion Policy\n\n"
            "Customer deletion requires explicit authorization from an administrator."
        ),
    },
]

documents = []


def reset_documents() -> None:
    documents.clear()
    documents.extend(
        document.copy()
        for document in DEFAULT_DOCUMENTS
    )


def add_document(document: dict) -> None:
    documents.append(document)


reset_documents()

from targets.rag.loader import load_text_file


def load_document_from_file(
    document_id: str,
    path: str,
) -> dict:

    content = load_text_file(path)

    return {
        "id": document_id,
        "content": content,
    }
