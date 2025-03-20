import os
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from typing import List, Optional
from langchain_core.documents import Document
from rag.embeddings import get_openai_embeddings

def setup_pinecone_vectorstore(
    documents: Optional[List[Document]] = None,
    embedding_model: Optional[object] = None,
    index_name: str = "langchain-doc-embeddings",
    namespace: Optional[str] = None,
    force_reload: bool = False
):
    """
    Setup a Pinecone vectorstore - creates new one or connects to existing.
    
    Args:
        documents: Optional list of Document objects to store
        embedding_model: Embedding model to use (if None, will use OpenAI embeddings)
        index_name: Name of the Pinecone index
        namespace: Optional namespace within the index
        force_reload: Whether to force reload the index with new documents
    
    Returns:
        A Pinecone vectorstore instance
    """
    # Use OpenAI embeddings by default if none provided
    if embedding_model is None:
        embedding_model = get_openai_embeddings()

    # Initialize Pinecone client
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY environment variable not set")
    
    pc = Pinecone(api_key=api_key)
    
    # Create index if it doesn't exist
    if index_name not in pc.list_indexes().names():
        print(f"Creating index {index_name}")
        pc.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embeddings dimension
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    else:
        print(f"Using existing index {index_name}")

    # Connect to the index
    pinecone_index = pc.Index(index_name)
    
    # Delete existing vectors if force_reload is True
    if force_reload and documents is not None:
        pinecone_index.delete(delete_all=True, namespace=namespace)
    
    # Create vectorstore
    vectorstore = PineconeVectorStore(
        index=pinecone_index,
        embedding=embedding_model,
        namespace=namespace,
        text_key="text"
    )
    
    # Add documents if provided
    if documents is not None:
        print(f"Adding {len(documents)} documents to Pinecone")
        vectorstore.add_documents(documents)
        
        # Verify documents were added
        stats = pinecone_index.describe_index_stats()
        print(f"Index stats after adding documents: {stats}")
    
    return vectorstore 