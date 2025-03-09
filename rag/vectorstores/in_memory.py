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
        embedding_model: Embedding model to use. If None, will raise ValueError.
    
    Returns:
        An InMemoryVectorStore instance
        
    Raises:
        ValueError: If embedding_model is None
    """
    if embedding_model is None:
        raise ValueError("embedding_model must be provided to create a vectorstore")
        
    return InMemoryVectorStore.from_documents(
        documents=documents,
        embedding=embedding_model
    ) 