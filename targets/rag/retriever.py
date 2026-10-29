from targets.rag.vector_store import search


def retrieve(query: str, store=None) -> list[dict]:
    if store is not None:
        return store.search(query)

    return search(query)
