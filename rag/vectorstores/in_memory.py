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
    
    # Create vectorstore
    vectorstore = InMemoryVectorStore(embedding=embedding_model)
    
    if documents:
        # Get existing document IDs if vectorstore already has documents
        existing_ids = set()
        if hasattr(vectorstore, '_docs'):
            existing_ids = {doc.metadata.get('doc_id') for doc in vectorstore._docs}
        
        # Filter out documents that already exist
        new_docs = [doc for doc in documents if doc.metadata.get('doc_id') not in existing_ids]
        
        if new_docs:
            print(f"Adding {len(new_docs)} new documents to in-memory vectorstore")
            vectorstore.add_documents(
                documents=new_docs,
                ids=[doc.metadata.get('doc_id') for doc in new_docs]
            )
        else:
            print("No new documents to add (all documents already exist)")
            
    return vectorstore 