from ollama import embed


EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(text: str) -> list[float]:
    response = embed(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.embeddings[0]
