from ollama import chat

from core.models.agent import AgentResult, RAGExecution
from targets.rag.retriever import retrieve
from targets.rag.vector_store import (
    add_document_to_vector_store,
    add_document_to_persistent_store,
    vector_store,
)
from targets.rag.storage import ChromaVectorStore

class RAGAgent:
    def __init__(
        self,
        document_id: str,
        document_path: str,
        persistent_store: ChromaVectorStore | None = None,
    ):
        self.model = "llama3.2:latest"
        self.persistent_store = persistent_store

        if self.persistent_store is not None:
            self.persistent_store.delete_document(document_id)

            add_document_to_persistent_store(
                store=self.persistent_store,
                document_id=document_id,
                path=document_path,
            )
        else:
            vector_store.clear()
            add_document_to_vector_store(
                document_id=document_id,
                path=document_path,
            )

    def run(self, user_input: str) -> AgentResult:
        try:
            if self.persistent_store is not None:
                documents = retrieve(
                    user_input,
                    store=self.persistent_store,
                )
            else:
                documents = retrieve(user_input)
        except Exception:
            return AgentResult(
                response="Document retrieval failed.",
                rag_execution=RAGExecution(
                    query=user_input,
                    retrieved_documents=[],
                    retrieval_succeeded=False,
                ),
            )

        context = "\n\n".join(
            document["content"] for document in documents
        )
        prompt = f"""Answer the user's question using the provided context.
Context:
{context}
User question:
{user_input}
"""
        response = chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )

        return AgentResult(
            response=response.message.content,
            rag_execution=RAGExecution(
                query=user_input,
                retrieved_documents=documents,
                retrieval_succeeded=True,
            ),
        )
