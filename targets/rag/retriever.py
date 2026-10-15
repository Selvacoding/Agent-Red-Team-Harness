from targets.rag.vector_store import search


def retrieve(query: str) -> list[dict]:
    return search(query)
