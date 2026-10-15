from ollama import chat

from core.models.agent import AgentResult, RAGExecution
from targets.rag.retriever import retrieve
from targets.rag.vector_store import (
    vector_store,
    add_document_to_vector_store,
)


class RAGAgent:
    def __init__(
        self,
        document_id: str,
        document_path: str,
    ):
        self.model = "llama3.2:latest"

        vector_store.clear()

        add_document_to_vector_store(
            document_id=document_id,
            path=document_path,
        )

    def run(self, user_input: str) -> AgentResult:

        documents = retrieve(user_input)

        context = "\n\n".join(
            document["content"]
            for document in documents
        )

        prompt = f"""
                    Answer the user's question using the provided context.

                    Context:
                    {context}

                    User question:
                    {user_input}
                """

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return AgentResult(
            response=response.message.content,
            rag_execution=RAGExecution(
                query=user_input,
                retrieved_documents=documents,
            ),
        )
