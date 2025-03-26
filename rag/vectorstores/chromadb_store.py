from typing import List
import chromadb
from langchain_core.documents import Document
from langchain_chroma import Chroma

def setup_chromadb_vectorstore(
    documents: List[Document],
    embedding_model: object,
    index_name: str = "langchain-doc-embeddings",
    persist_directory: str = "./chroma_db"
) -> Chroma:
    """
    Create or get a ChromaDB vectorstore
    
    Args:
        documents: List of Document objects to store
        embedding_model: Embedding model to use for generating vectors
        index_name: Name of the collection
        persist_directory: Directory to persist the ChromaDB data
    
    Returns:
        A Chroma vectorstore instance
    """
    # Create persistent client
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Create or get collection
    vectorstore = Chroma(
        client=client,
        collection_name=index_name,
        embedding_function=embedding_model,
    )
    
    # Add documents if provided
    if documents:
        vectorstore.add_documents(documents)
        
    return vectorstore 