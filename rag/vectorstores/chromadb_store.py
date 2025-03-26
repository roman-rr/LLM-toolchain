from typing import List
import chromadb
from langchain_core.documents import Document
from langchain_chroma import Chroma

def setup_chromadb_vectorstore(
    documents: List[Document],
    embedding_model: object,
    index_name: str = "langchain-doc-embeddings",
    collection_name: str = None,
    persist_directory: str = "./chroma_db",
    force_reload: bool = False
) -> Chroma:
    """
    Create or get a ChromaDB vectorstore
    
    Args:
        documents: List of Document objects to store
        embedding_model: Embedding model to use for generating vectors
        index_name: Name of the collection (deprecated, use collection_name instead)
        collection_name: Name of the collection for multi-user isolation
        persist_directory: Directory to persist the ChromaDB data
        force_reload: Whether to force reload the collection with new documents
    
    Returns:
        A Chroma vectorstore instance
    """
    # Create persistent client
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Use collection_name if provided, otherwise fall back to index_name
    collection_name = collection_name or index_name
    
    # Delete collection if force reload is True
    if force_reload:
        try:
            client.delete_collection(name=collection_name)
            print(f"Deleted existing collection: {collection_name}")
        except ValueError:
            # Collection doesn't exist, that's fine
            pass
    
    # Create or get collection
    vectorstore = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embedding_model,
    )
    
    # Add documents if provided
    if documents:
        print(f"Adding {len(documents)} documents to collection: {collection_name}")
        vectorstore.add_documents(documents)
        
    return vectorstore 