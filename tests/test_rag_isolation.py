from targets.rag.documents import documents, reset_documents
from targets.rag.poison import poison_document
from targets.rag.vector_store import (
    vector_store,
    build_vector_store,
    reset_vector_store,
)


build_vector_store()


def print_state(label: str) -> None:
    print(f"\n{label}")

    print(
        "Documents:",
        [document["id"] for document in documents],
    )

    print("Vector store:")

    for document in vector_store:
        print(
            " ",
            document["id"],
            document["metadata"],
        )


print_state("Initial state")

poison_document("Poison A")

print_state("After Poison A")

reset_documents()
reset_vector_store()

print_state("After reset")

poison_document("Poison B")

print_state("After Poison B")
