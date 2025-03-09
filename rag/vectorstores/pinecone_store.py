import os
from pinecone import Pinecone, ServerlessSpec
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from typing import List, Optional
from langchain_core.documents import Document
from rag.embeddings import get_openai_embeddings

def create_pinecone_vectorstore(
    documents: List[Document],
    index_name: str = "langchain-doc-embeddings",
    namespace: Optional[str] = None,
    embedding_model: object,
    force_reload: bool = False
):
    """
    Create a Pinecone vectorstore from documents.
    
    Args:
        documents: List of Document objects to store
        index_name: Name of the Pinecone index
        namespace: Optional namespace within the index
        embedding_model: Embedding model to use
        force_reload: Whether to force reload the index with new documents
    
    Returns:
        A Pinecone vectorstore instance
    """
    # Check if embedding model is provided
    if embedding_model is None:
        raise ValueError("embedding_model must be provided")
        
    # Create an instance of the Pinecone class
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY environment variable not set")
        
    pc = Pinecone(api_key=api_key)

    # Create the Pinecone index if it doesn't exist
    if index_name not in pc.list_indexes().names():
        print(f"Creating index {index_name}")
        pc.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embeddings dimension
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    else:
        print(f"Index {index_name} already exists")

    # Connect to the Pinecone index
    pinecone_index = pc.Index(index_name)
    
    # If force_reload is False and index exists with data, return existing vectorstore
    if not force_reload and pinecone_index.describe_index_stats().total_vector_count > 0:
        return LangchainPinecone.from_existing_index(
            index_name=index_name,
            embedding=embedding_model,
            namespace=namespace
        )

    # Delete existing vectors before updating if force_reload is True
    if force_reload:
        pinecone_index.delete(delete_all=True, namespace=namespace)
    
    # Create vectorstore from documents
    return LangchainPinecone.from_documents(
        documents=documents,
        embedding=embedding_model,
        index_name=index_name,
        namespace=namespace
    )

def get_existing_pinecone_vectorstore(
    index_name: str = "langchain-doc-embeddings",
    namespace: Optional[str] = None,
    embedding_model: object
):
    """
    Connect to an existing Pinecone vectorstore without adding new documents.
    
    Args:
        index_name: Name of the Pinecone index
        namespace: Optional namespace within the index
        embedding_model: Embedding model to use
    
    Returns:
        A Pinecone vectorstore instance
    """
    # Check if embedding model is provided
    if embedding_model is None:
        raise ValueError("embedding_model must be provided")
        
    return LangchainPinecone.from_existing_index(
        index_name=index_name,
        embedding=embedding_model,
        namespace=namespace
    ) 