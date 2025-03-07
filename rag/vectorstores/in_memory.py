from langchain_core.vectorstores import InMemoryVectorStore
from typing import List, Optional
from langchain_core.documents import Document
from rag.embeddings import get_openai_embeddings

def create_in_memory_vectorstore(
    documents: List[Document],
    embedding_model: Optional[object] = None
):
    """
    Create an InMemoryVectorStore from documents.
    
    Args:
        documents: List of Document objects to store
        embedding_model: Embedding model to use (defaults to OpenAIEmbeddings)
    
    Returns:
        An InMemoryVectorStore instance
    """
    embedding_model = embedding_model or get_openai_embeddings()
    
    return InMemoryVectorStore.from_documents(
        documents=documents,
        embedding=embedding_model
    ) 