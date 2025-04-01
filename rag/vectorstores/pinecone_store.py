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
        namespace: Optional namespace for multi-user isolation within the index
        force_reload: Whether to force reload the namespace with new documents
    
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
    
    # Delete existing vectors in the namespace if force_reload is True
    if force_reload and documents is not None and namespace:
        print(f"Deleting existing vectors in namespace: {namespace}")
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
        if force_reload and namespace:
            print(f"Deleting existing vectors in namespace: {namespace}")
            pinecone_index.delete(delete_all=True, namespace=namespace)
        elif documents:
            # Get existing IDs
            existing_ids = set()
            query_response = pinecone_index.query(
                vector=[0] * 1536,  # dummy vector
                namespace=namespace,
                top_k=10000,
                include_metadata=True
            )
            for match in query_response.matches:
                existing_ids.add(match.id)
            
            # Filter out existing documents
            new_docs = [doc for doc in documents if doc.metadata.get('doc_id') not in existing_ids]
            
            if new_docs:
                print(f"Adding {len(new_docs)} new documents to Pinecone{' in namespace ' + namespace if namespace else ''}")
                vectorstore.add_documents(new_docs)
        
        # Verify documents were added
        stats = pinecone_index.describe_index_stats()
        if namespace:
            namespace_count = stats.namespaces.get(namespace, {}).get('vector_count', 0)
            print(f"Namespace '{namespace}' vector count: {namespace_count}")
        else:
            print(f"Index stats after adding documents: {stats}")
    
    return vectorstore 