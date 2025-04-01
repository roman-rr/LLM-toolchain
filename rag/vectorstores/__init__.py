from enum import Enum
from typing import List, Optional, Any
from langchain_core.documents import Document
import os

from rag.embeddings import get_openai_embeddings
from rag.vectorstores.in_memory import create_in_memory_vectorstore
from rag.vectorstores.pinecone_store import setup_pinecone_vectorstore
from rag.vectorstores.chromadb_store import setup_chromadb_vectorstore

# Define an enum for vectorstore types
class VectorStoreType(str, Enum):
    IN_MEMORY = "in_memory"
    PINECONE = "pinecone"
    CHROMA = "chroma"
    FAISS = "faiss"

def get_vectorstore(
    documents: List[Document], 
    embedding_model: object,
    namespace: Optional[str] = None,
    collection_name: Optional[str] = None,
    vectorstore_type: VectorStoreType = VectorStoreType.IN_MEMORY,
    index_name: str = "langchain-doc-embeddings",
    force_reload: bool = False,
    persist_directory: str = "./faiss_indexes"
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
            namespace=namespace,
            collection_name=collection_name,
            index_name=index_name,
            force_reload=force_reload
        )
    elif vectorstore_type == VectorStoreType.CHROMA:
        return setup_chromadb_vectorstore(
            documents=documents,
            embedding_model=embedding_model,
            namespace=namespace,
            collection_name=collection_name,
            index_name=index_name,
            force_reload=force_reload
        )
    elif vectorstore_type == VectorStoreType.FAISS:
        from rag.vectorstores.faiss_store import setup_faiss_vectorstore
        return setup_faiss_vectorstore(
            documents=documents,
            embedding_model=embedding_model,
            index_name=index_name,
            persist_directory=persist_directory,
            force_reload=force_reload
        )
    else:
        raise ValueError(f"Unsupported vectorstore type: {vectorstore_type}") 