from enum import Enum
from typing import List, Optional
from langchain_core.documents import Document

from rag.embeddings import get_openai_embeddings
from rag.vectorstores.in_memory import create_in_memory_vectorstore
from rag.vectorstores.pinecone_store import setup_pinecone_vectorstore

# Define an enum for vectorstore types
class VectorStoreType(str, Enum):
    IN_MEMORY = "in_memory"
    PINECONE = "pinecone"

def get_vectorstore(
    documents: List[Document], 
    embedding_model: object,
    vectorstore_type: VectorStoreType = VectorStoreType.IN_MEMORY,
    index_name: str = "langchain-doc-embeddings",
    force_reload: bool = False
):
    """
    Create or get a vectorstore based on the specified type
    
    Args:
        documents: List of Document objects to store
        embedding_model: Embedding model to use. If None, will use OpenAI embeddings
        vectorstore_type: Type of vectorstore to create (IN_MEMORY or PINECONE)
        index_name: Name of the index (for Pinecone)
        force_reload: Whether to force reload the index with new documents (for Pinecone)
    
    Returns:
        A vectorstore instance
        
    Raises:
        ValueError: If vectorstore_type is not supported
    """
    # if embedding_model is None:
    #     embedding_model = get_openai_embeddings()
        
    if vectorstore_type == VectorStoreType.IN_MEMORY:
        # In-memory store doesn't support appending, always creates new store
        return create_in_memory_vectorstore(documents=documents, embedding_model=embedding_model)
    elif vectorstore_type == VectorStoreType.PINECONE:
        return setup_pinecone_vectorstore(
            documents=documents,
            embedding_model=embedding_model,
            index_name=index_name,
            force_reload=force_reload
        )
    else:
        raise ValueError(f"Unsupported vectorstore type: {vectorstore_type}") 